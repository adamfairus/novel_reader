#!/usr/bin/env python3
"""
generate_manifest.py — Generate lightweight static JSON manifest of novel chapters.
Dipakai oleh API `/api/chapters/[slug]` saat di-deploy (misal di Vercel),
sehingga daftar chapter tetap muncul lengkap & cepat tanpa harus membaca filesystem serverless.
"""

import json
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "src" / "data"
OUTPUT_FILE = OUTPUT_DIR / "chapters-manifest.json"

NOVELS = [
    {"slug": "myst-might-mayhem", "folder": "Myst Might Mayhem"},
    {"slug": "the-heavenly-demon-cant-live-a-normal-life", "folder": "The Heavenly Demon"},
    {"slug": "star-embracing-swordmaster", "folder": "Star Embracing Swordmaster"},
]


def parse_ch_sort(fn: str):
    m = re.match(r"Chapter\s*0*(\d+)(?:\.(\d+))?", fn, re.I)
    if not m:
        return (0, -1)
    maj = int(m.group(1))
    min_ = int(m.group(2)) if m.group(2) is not None else -1
    return (maj, min_)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {}

    for n in NOVELS:
        slug = n["slug"]
        folder = BASE_DIR / n["folder"]
        if not folder.exists():
            print(f"[!] Folder tidak ditemukan: {folder}")
            continue

        files = sorted(
            [f.name for f in folder.glob("*.md")],
            key=lambda fn: parse_ch_sort(fn),
        )

        chapter_list = []
        for f in files:
            m_ch = re.match(
                r"^Chapter\s*0*(\d+(?:\.\d+)?)(?:\s*[-–:_]\s*(.*))?\.md$", f, re.I
            )
            if m_ch:
                raw_num = m_ch.group(1)
                sub = (m_ch.group(2) or "").strip()
                idx = float(raw_num) if "." in raw_num else int(raw_num)
                label = f"Chapter {raw_num}"
                disp = f"Chapter {raw_num}: {sub}" if sub else label
                chapter_list.append(
                    {
                        "index": idx,
                        "label": label,
                        "subtitle": sub,
                        "displayTitle": disp,
                        "filename": f,
                    }
                )
            else:
                m = re.match(r"^(\d+)\s*-\s*(.+)\.md$", f)
                idx = int(m.group(1)) if m else 0
                title = m.group(2).replace("_", ":") if m else f.replace(".md", "")
                chapter_list.append(
                    {
                        "index": idx,
                        "label": f"Chapter {idx}",
                        "subtitle": title,
                        "displayTitle": f"Chapter {idx}: {title}",
                        "filename": f,
                    }
                )

        manifest[slug] = chapter_list
        print(f"[*] {slug}: {len(chapter_list)} chapter dipetakan.")

    OUTPUT_FILE.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    kb_size = len(OUTPUT_FILE.read_bytes()) / 1024
    print(f"\n[✓] Sukses membuat manifest: {OUTPUT_FILE} ({kb_size:.1f} KB)")


if __name__ == "__main__":
    main()
