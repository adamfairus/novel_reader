-- Arcana Reader - Supabase Database Schema
-- Jalankan query ini di Supabase SQL Editor jika ingin mengaktifkan sinkronisasi database

-- 1. Tabel Novels
CREATE TABLE IF NOT EXISTS public.novels (
    id TEXT PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    cover_url TEXT,
    total_chapters INT DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Tabel Chapters (Metadata chapter, konten tetap di Cloudflare R2)
CREATE TABLE IF NOT EXISTS public.chapters (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    novel_slug TEXT REFERENCES public.novels(slug) ON DELETE CASCADE,
    chapter_index INT NOT NULL,
    title TEXT NOT NULL,
    r2_key TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(novel_slug, chapter_index)
);

-- 3. Tabel Reading Progress (Bookmark & Riwayat Baca Terakhir)
CREATE TABLE IF NOT EXISTS public.reading_progress (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID, -- Opsional, jika menggunakan Supabase Auth
    device_id TEXT NOT NULL, -- ID perangkat untuk pembaca tanpa login
    novel_slug TEXT REFERENCES public.novels(slug) ON DELETE CASCADE,
    last_chapter_index INT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(device_id, novel_slug)
);

-- Aktifkan Row Level Security (RLS)
ALTER TABLE public.novels ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reading_progress ENABLE ROW LEVEL SECURITY;

-- Policy: Publik bisa membaca katalog & chapter
CREATE POLICY "Public Read Novels" ON public.novels FOR SELECT USING (true);
CREATE POLICY "Public Read Chapters" ON public.chapters FOR SELECT USING (true);
CREATE POLICY "Public Manage Progress" ON public.reading_progress FOR ALL USING (true);
