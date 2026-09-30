# 📖 Novel Reader

Web reader minimalis, cepat, dan elegan yang dibangun dengan **Astro 5**, **Tailwind CSS**, **Cloudflare R2**, dan **Supabase**. Didesain dengan standar tinggi **Impeccable Design System** (Zero AI Slop, ergonomi membaca optimal, dan performa tinggi).

---

## ✨ Fitur Utama

- **🚀 Ultra-Ringan & Cepat:** Berbasis Astro dengan rendering serverless/edge cepat.
- **🎨 Impeccable Typography & Ergonomi:**
  - Lebar kolom baca terkunci di **72ch** (*optimal reading measure* agar mata tidak lelah).
  - Tipografi editorial buku: Font Serif elegan (*Newsreader*) untuk cerita, dipadu Sans modern (*Plus Jakarta Sans*) untuk kontrol antarmuka.
  - **4 Tema Membaca:** *Obsidian Dark* (default arang mendalam), *OLED Pure Black* (hemat baterai layar AMOLED), *Warm Sepia* (kertas novel klasik), dan *Light*.
- **🌐 Terjemahan Instan On-The-Fly (EN ⇄ ID):**
  - Tombol toggle satu klik untuk menerjemahkan chapter dari Bahasa Inggris ke Bahasa Indonesia secara langsung di browser tanpa perlu reload halaman.
  - Caching terjemahan di `sessionStorage` agar pergantian bahasa instan tanpa kuota ganda.
- **⌨️ Keyboard Shortcuts:**
  - `←` (Panah Kiri): Chapter Sebelumnya
  - `→` (Panah Kanan): Chapter Selanjutnya
  - `T`: Toggle Terjemahan Bahasa Indonesia
- **💾 Auto-Save Reading Progress:**
  - Otomatis mengingat chapter terakhir yang kamu baca untuk setiap novel.
- **🗄️ Arsitektur Storage Terpisah:**
  - Kode website terisolasi dan super ringan di Git/GitHub.
  - Ribuan file teks chapter disimpan efisien di **Cloudflare R2** (*zero egress bandwidth cost*).
  - Metadata dan riwayat baca tersimpan di **Supabase**.

---

## 🚀 Menjalankan Secara Lokal

```bash
# 1. Jalankan development server
npm run dev

# 2. Buka di browser
# http://localhost:4321
```

*(Dalam mode lokal, web reader dapat langsung membaca folder Markdown lokal yang ada di direktori ini tanpa harus upload ke Cloudflare R2 terlebih dahulu).*

---

## ☁️ Konfigurasi Cloudflare R2 & Supabase

Salin file template environment:
```bash
cp .env.example .env.local
```

Isi variabel di `.env.local`:
```env
PUBLIC_SUPABASE_URL=https://your-project.supabase.co
PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
PUBLIC_R2_URL=https://pub-your-id.r2.dev

# Diperlukan untuk script uploader lokal:
R2_ACCOUNT_ID=your-cloudflare-account-id
R2_ACCESS_KEY_ID=your-r2-access-key-id
R2_SECRET_ACCESS_KEY=your-r2-secret-access-key
R2_BUCKET_NAME=novel-reader
```

### 1. Setup Database Supabase
Buka **SQL Editor** di dashboard Supabase kamu, lalu jalankan query dari [`scripts/supabase_schema.sql`](scripts/supabase_schema.sql).

### 2. Upload Novel ke Cloudflare R2 & Supabase
Gunakan script Python zero-dependency yang sudah disediakan:
```bash
# Simulasi (Dry Run)
python3 scripts/sync_to_r2_supabase.py --dry-run

# Upload ke Cloudflare R2 saja
python3 scripts/sync_to_r2_supabase.py --r2

# Sinkronkan metadata ke Supabase saja
python3 scripts/sync_to_r2_supabase.py --supabase

# Jalankan keduanya
python3 scripts/sync_to_r2_supabase.py --all
```

---

## 🚀 Deploy ke Vercel

1. Commit dan push proyek ini ke GitHub:
   ```bash
   git add .
   git commit -m "feat: initial novel reader setup"
   git branch -M main
   # git remote add origin https://github.com/adamfairus/<repo-name>.git
   # git push -u origin main
   ```
2. Hubungkan repository GitHub kamu ke **Vercel**.
3. Di dashboard Vercel, masukkan Environment Variables dari `.env.local`:
   - `PUBLIC_SUPABASE_URL`
   - `PUBLIC_SUPABASE_ANON_KEY`
   - `PUBLIC_R2_URL`
4. Selesai! Web app akan otomatis ter-deploy di Vercel dengan performa CDN global.
