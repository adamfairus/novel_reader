import type { APIRoute } from 'astro';
import fs from 'node:fs';
import path from 'node:path';

const SLUG_TO_FOLDER: Record<string, string> = {
  'myst-might-mayhem': 'Myst Might Mayhem',
  'the-heavenly-demon-cant-live-a-normal-life': 'The Heavenly Demon',
  'star-embracing-swordmaster': 'Star Embracing Swordmaster',
};

export const GET: APIRoute = async ({ request }) => {
  const url = new URL(request.url);
  const slug = url.searchParams.get('slug');
  const chapterParam = url.searchParams.get('chapter');

  if (!slug || !chapterParam) {
    return new Response(JSON.stringify({ error: 'Parameter slug dan chapter wajib diisi' }), { status: 400 });
  }

  const r2BaseUrl = import.meta.env.PUBLIC_R2_URL || '';

  // 1. Jika Cloudflare R2 URL sudah diset dan valid, fetch dari R2
  if (r2BaseUrl && !r2BaseUrl.includes('your-id')) {
    try {
      const r2Url = `${r2BaseUrl.replace(/\/$/, '')}/novels/${slug}/${chapterParam}.md`;
      const res = await fetch(r2Url);
      if (res.ok) {
        const text = await res.text();
        return new Response(JSON.stringify({ slug, chapter: chapterParam, content: text }), {
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch {
      // fallback ke lokal
    }
  }

  // 2. Baca dari folder lokal (dev mode & fallback sebelum deploy R2)
  const folderName = SLUG_TO_FOLDER[slug];
  if (folderName) {
    const localDir = path.resolve(process.cwd(), folderName);
    if (fs.existsSync(localDir)) {
      const files = fs.readdirSync(localDir);
      // cari file yang cocok dengan nomor index atau nama file
      const targetFile = files.find((f) => {
        if (f === chapterParam || f === `${chapterParam}.md`) return true;
        const match = f.match(/^(\d+)\s*-/);
        return match && parseInt(match[1], 10) === parseInt(chapterParam, 10);
      });

      if (targetFile) {
        const fullPath = path.join(localDir, targetFile);
        const text = fs.readFileSync(fullPath, 'utf-8');
        return new Response(JSON.stringify({ slug, chapter: chapterParam, content: text, filename: targetFile }), {
          headers: { 'Content-Type': 'application/json' },
        });
      }
    }
  }

  return new Response(JSON.stringify({ error: 'Chapter tidak ditemukan' }), { status: 404 });
};
