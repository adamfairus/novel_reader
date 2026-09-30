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
  label: string;
  subtitle: string;
  displayTitle: string;
  filename: string;
}

export function parseChapterTitle(index: number, raw: string): { label: string; subtitle: string; displayTitle: string } {
  const t = raw.replace(/_/g, ':').trim();

  // Ambil nomor chapter asli (dukung desimal seperti 498.9)
  const numMatch = t.match(/Chapter\s*#?\s*(\d+(?:\.\d+)?)/i);
  const chNum = numMatch ? numMatch[1] : String(index);
  const label = `Chapter ${chNum}`;

  // Bersihkan pola ganda dari translator seperti 'Chapter 82 - 105 - Don't mess with moles (1)'
  const sub = t.replace(/^Chapter\s*#?\s*\d+(?:\.\d+)?\s*(?:[-–:]\s*\d+\s*)?[-–:]\s*/i, '').trim();

  if (!sub || /^Chapter\b/i.test(sub)) {
    return { label, subtitle: '', displayTitle: label };
  }

  return { label, subtitle: sub, displayTitle: `${label}: ${sub}` };
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
        const chapters: ChapterItem[] = data.map((d) => {
          const parsed = parseChapterTitle(d.chapter_index, d.title);
          return {
            index: d.chapter_index,
            ...parsed,
            filename: d.r2_key,
          };
        });
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
        const parsed = parseChapterTitle(index, rawTitle);
        return {
          index,
          ...parsed,
          filename,
        };
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
