#!/usr/bin/env python3
"""
sync_to_r2_supabase.py — Script upload file novel ke Cloudflare R2 dan sinkronisasi metadata ke Supabase.

Fitur:
  - Zero-dependency: menggunakan Python standard library (urllib, hashlib, hmac)
  - Mengupload file .md ke Cloudflare R2 (S3-compatible API dengan SigV4)
  - Menyinkronkan daftar novel dan metadata chapter ke database Supabase via REST API
  - Mode dry-run untuk simulasi sebelum upload nyata

Penggunaan:
    # 1. Cek persiapan (dry-run)
    python3 scripts/sync_to_r2_supabase.py --dry-run

    # 2. Upload ke Cloudflare R2 saja
    python3 scripts/sync_to_r2_supabase.py --r2

    # 3. Sinkronkan metadata ke Supabase saja
    python3 scripts/sync_to_r2_supabase.py --supabase

    # 4. Sinkronkan keduanya sekaligus
    python3 scripts/sync_to_r2_supabase.py --all
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import hmac
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# Load konfigurasi dari .env.local jika ada
ENV_LOCAL = Path(".env.local")
if ENV_LOCAL.exists():
    for line in ENV_LOCAL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

NOVEL_MAPPING = [
    {
        "id": "myst-might-mayhem",
        "slug": "myst-might-mayhem",
        "title": "Myst, Might, Mayhem",
        "author": "Midwinter Moonlight (한중월야)",
        "cover_url": "https://images.novelping.com/novel/myst-might-mayhem.jpg",
        "folder": "Myst Might Mayhem",
    },
    {
        "id": "the-heavenly-demon-cant-live-a-normal-life",
        "slug": "the-heavenly-demon-cant-live-a-normal-life",
        "title": "The Heavenly Demon Can't Live a Normal Life",
        "author": "Sancheon",
        "cover_url": "https://images.novelping.com/novel/the-heavenly-demon-cant-live-a-normal-life.jpg",
        "folder": "The Heavenly Demon",
    },
    {
        "id": "star-embracing-swordmaster",
        "slug": "star-embracing-swordmaster",
        "title": "Star Embracing Swordmaster",
        "author": "Q10",
        "cover_url": "https://images.novelping.com/novel/star-embracing-swordmaster.jpg",
        "folder": "Star Embracing Swordmaster",
    },
]


def sign(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def get_signature_key(key: str, date_stamp: str, region: str, service: str) -> bytes:
    k_date = sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    return sign(k_service, "aws4_request")


def upload_file_to_r2(
    file_path: Path,
    r2_key: str,
    account_id: str,
    access_key: str,
    secret_key: str,
    bucket: str,
) -> bool:
    """Upload satu file ke Cloudflare R2 menggunakan AWS S3 SigV4 murni."""
    method = "PUT"
    service = "s3"
    region = "auto"
    host = f"{bucket}.{account_id}.r2.cloudflarestorage.com"
    endpoint = f"https://{host}/{r2_key}"

    t = datetime.datetime.now(datetime.timezone.utc)
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")

    data = file_path.read_bytes()
    content_hash = hashlib.sha256(data).hexdigest()

    canonical_uri = "/" + urllib.parse.quote(r2_key)
    canonical_headers = (
        f"host:{host}\n"
        f"x-amz-content-sha256:{content_hash}\n"
        f"x-amz-date:{amz_date}\n"
    )
    signed_headers = "host;x-amz-content-sha256;x-amz-date"
    canonical_request = (
        f"{method}\n{canonical_uri}\n\n{canonical_headers}\n{signed_headers}\n{content_hash}"
    )

    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = (
        f"AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n"
        + hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    )

    signing_key = get_signature_key(secret_key, date_stamp, region, service)
    signature = hmac.new(
        signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    auth_header = (
        f"AWS4-HMAC-SHA256 Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    headers = {
        "Content-Type": "text/markdown; charset=utf-8",
        "x-amz-date": amz_date,
        "x-amz-content-sha256": content_hash,
        "Authorization": auth_header,
    }

    req = urllib.request.Request(endpoint, data=data, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        print(f"    ! Gagal upload {r2_key}: {e}", file=sys.stderr)
        return False


def sync_novel_to_supabase(
    novel: dict, chapters: list[dict], supabase_url: str, supabase_key: str
) -> bool:
    """Kirim metadata novel dan daftar chapter ke Supabase via REST API."""
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

    # 1. Upsert novel
    novel_payload = {
        "id": novel["id"],
        "slug": novel["slug"],
        "title": novel["title"],
        "author": novel["author"],
        "cover_url": novel["cover_url"],
        "total_chapters": len(chapters),
    }

    req = urllib.request.Request(
        f"{supabase_url.rstrip('/')}/rest/v1/novels",
        data=json.dumps(novel_payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status not in (200, 201, 204):
                return False
    except Exception as e:
        print(f"    ! Gagal upsert novel ke Supabase: {e}", file=sys.stderr)
        return False

    # 2. Upsert chapters per batch 100
    batch_size = 100
    for i in range(0, len(chapters), batch_size):
        batch = chapters[i : i + batch_size]
        req_ch = urllib.request.Request(
            f"{supabase_url.rstrip('/')}/rest/v1/chapters",
            data=json.dumps(batch).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req_ch, timeout=30) as resp_ch:
                pass
        except Exception as e:
            print(f"    ! Gagal batch chapter {i}: {e}", file=sys.stderr)
            return False

    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Upload novel ke Cloudflare R2 & Supabase")
    ap.add_argument("--r2", action="store_true", help="upload file chapter ke Cloudflare R2")
    ap.add_argument("--supabase", action="store_true", help="sinkronkan metadata ke Supabase")
    ap.add_argument("--all", action="store_true", help="jalankan R2 + Supabase")
    ap.add_argument("--dry-run", action="store_true", help="simulasi tanpa mengirim data")
    args = ap.parse_args()

    do_r2 = args.r2 or args.all
    do_supabase = args.supabase or args.all

    if not do_r2 and not do_supabase and not args.dry_run:
        ap.print_help()
        print("\nContoh cepat: python3 scripts/sync_to_r2_supabase.py --dry-run")
        return 1

    r2_acc = os.environ.get("R2_ACCOUNT_ID", "")
    r2_key = os.environ.get("R2_ACCESS_KEY_ID", "")
    r2_sec = os.environ.get("R2_SECRET_ACCESS_KEY", "")
    r2_bucket = os.environ.get("R2_BUCKET_NAME", "novel-reader")
    sb_url = os.environ.get("PUBLIC_SUPABASE_URL", "")
    sb_key = os.environ.get("PUBLIC_SUPABASE_ANON_KEY", "")

    print("=== Persiapan Sinkronisasi Novel ===")
    for n in NOVEL_MAPPING:
        folder_path = Path(n["folder"])
        if not folder_path.exists():
            print(f"[!] Folder {n['folder']} tidak ditemukan di direktori saat ini.")
            continue

        files = sorted(folder_path.glob("*.md"))
        print(f"\n[*] {n['title']} ({len(files)} chapter)")

        chapters_meta = []
        for f in files:
            m_ch = re.match(r"^Chapter\s*0*(\d+(?:\.\d+)?)(?:\s*[-–:_]\s*(.*))?\.md$", f.name, re.I)
            if m_ch:
                idx = int(float(m_ch.group(1)))
                sub = (m_ch.group(2) or "").strip()
                title = f"Chapter {idx}: {sub}" if sub else f"Chapter {idx}"
            else:
                m = re.match(r"^(\d+)\s*-\s*(.+)\.md$", f.name)
                idx = int(m.group(1)) if m else 0
                title = m.group(2).replace("_", ":") if m else f.stem
            r2_target_key = f"novels/{n['slug']}/{idx}.md"

            chapters_meta.append({
                "novel_slug": n["slug"],
                "chapter_index": idx,
                "title": title,
                "r2_key": r2_target_key,
            })

            if do_r2 and not args.dry_run:
                if not (r2_acc and r2_key and r2_sec):
                    print("    ! Kredensial R2 belum lengkap di .env.local", file=sys.stderr)
                    return 1
                ok = upload_file_to_r2(f, r2_target_key, r2_acc, r2_key, r2_sec, r2_bucket)
                if ok:
                    print(f"    + R2: {r2_target_key}")

        if do_supabase and not args.dry_run:
            if not (sb_url and sb_key):
                print("    ! Kredensial Supabase belum lengkap di .env.local", file=sys.stderr)
                return 1
            ok = sync_novel_to_supabase(n, chapters_meta, sb_url, sb_key)
            if ok:
                print(f"    + Supabase: metadata {n['title']} berhasil disinkronkan.")

    if args.dry_run:
        print("\n[✓] Simulasi Dry-Run selesai! Semua file terpetakan dengan benar.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
