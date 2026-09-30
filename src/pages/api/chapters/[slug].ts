import type { APIRoute } from 'astro';
import fs from 'node:fs';
import path from 'node:path';
import { supabase, isSupabaseConfigured } from '../../../lib/supabase';

const SLUG_TO_FOLDER: Record<string, string> = {
  'myst-might-mayhem': 'Myst Might Mayhem',
  'the-heavenly-demon-cant-live-a-normal-life': 'The Heavenly Demon',
  'star-embracing-swordmaster': 'Star Embracing Swordmaster',
};

export interface ChapterItem {
  index: number;
  title: string;
  filename: string;
}

export const GET: APIRoute = async ({ params }) => {
  const slug = params.slug;
  if (!slug) {
    return new Response(JSON.stringify({ error: 'Slug tidak ditemukan' }), { status: 400 });
  }

  // 1. Coba dari Supabase jika aktif
  if (isSupabaseConfigured && supabase) {
    try {
      const { data, error } = await supabase
        .from('chapters')
        .select('chapter_index, title, r2_key')
        .eq('novel_slug', slug)
        .order('chapter_index', { ascending: true });

      if (!error && data && data.length > 0) {
        const chapters: ChapterItem[] = data.map((d) => ({
          index: d.chapter_index,
          title: d.title,
          filename: d.r2_key,
        }));
        return new Response(JSON.stringify(chapters), {
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch {
      // lanjut fallback ke file lokal
    }
  }

  // 2. Fallback baca dari folder lokal jika masih dalam dev / sebelum upload ke R2
  const folderName = SLUG_TO_FOLDER[slug];
  if (folderName) {
    const localDir = path.resolve(process.cwd(), folderName);
    if (fs.existsSync(localDir)) {
      const files = fs.readdirSync(localDir).filter((f) => f.endsWith('.md')).sort();
      const chapters: ChapterItem[] = files.map((filename) => {
        const match = filename.match(/^(\d+)\s*-\s*(.+)\.md$/);
        const index = match ? parseInt(match[1], 10) : 0;
        const rawTitle = match ? match[2] : filename.replace(/\.md$/, '');
        // kembalikan underscore ke karakter aslinya jika ada
        const title = rawTitle.replace(/_/g, ':');
        return { index, title, filename };
      });

      return new Response(JSON.stringify(chapters), {
        headers: { 'Content-Type': 'application/json' },
      });
    }
  }

  return new Response(JSON.stringify([]), {
    headers: { 'Content-Type': 'application/json' },
  });
};
