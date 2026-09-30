#!/usr/bin/env python3
"""
Skrip untuk merapikan nama file dan header Markdown di folder 'Star Embracing Swordmaster'.
Menghapus penomoran RAW Korea yang redundant (- 24 -, - 25 -, dsb)
dan menstandardisasi format nama file menjadi:
  001 - Chapter 1 - Because I didn’t surrender (1).md
  002 - Chapter 2 - Because I didn’t surrender (2).md
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TARGET_DIR = BASE_DIR / "Star Embracing Swordmaster"


def clean_novel_files():
    if not TARGET_DIR.exists():
        print(f"[!] Folder tidak ditemukan: {TARGET_DIR}")
        return

    files = sorted([f for f in os.listdir(TARGET_DIR) if f.endswith(".md")])
    total = len(files)
    print(f"[*] Menemukan {total} file di '{TARGET_DIR.name}'...")

    renamed_count = 0
    header_updated_count = 0

    for f in files:
        old_path = TARGET_DIR / f
        stem = f[:-3]
        parts = stem.split(" - ")
        p_num = parts[0]
        try:
            ch_idx = int(p_num)
        except ValueError:
            print(f"[!] Lewati (prefix bukan angka): {f}")
            continue

        rest = " - ".join(parts[1:])

        # Bersihkan awalan Chapter X dan nomor raw Korea
        s = rest
        s = re.sub(r"^Chapter\s*\d+\s*[_\-:]\s*", "", s, flags=re.I)
        s = re.sub(r"^\d+\s*[-–:]\s*", "", s)
        s = s.strip()

        new_fn = f"{ch_idx:03d} - Chapter {ch_idx} - {s}.md" if s else f"{ch_idx:03d} - Chapter {ch_idx}.md"
        new_header = f"# Chapter {ch_idx}: {s}" if s else f"# Chapter {ch_idx}"
        new_path = TARGET_DIR / new_fn

        # 1. Update line 1 di file jika diawali '# '
        content = old_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        if lines and lines[0].startswith("# "):
            if lines[0] != new_header:
                lines[0] = new_header
                old_path.write_text("\n".join(lines), encoding="utf-8")
                header_updated_count += 1

        # 2. Rename file jika namanya berubah
        if old_path != new_path:
            old_path.rename(new_path)
            renamed_count += 1

    remaining_files = sorted([f for f in os.listdir(TARGET_DIR) if f.endswith(".md")])
    print(f"[✓] Selesai!")
    print(f"    - Total file diproses: {total}")
    print(f"    - File direname: {renamed_count}")
    print(f"    - Header # Chapter diupdate: {header_updated_count}")
    print(f"    - Total file sekarang: {len(remaining_files)}")


if __name__ == "__main__":
    clean_novel_files()
