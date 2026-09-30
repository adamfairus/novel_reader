import type { APIRoute } from 'astro';

async function translateChunk(text: string): Promise<string> {
  if (!text || text.trim() === '') return text;
  try {
    const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=id&dt=t&q=${encodeURIComponent(text)}`;
    const res = await fetch(url);
    if (!res.ok) return text;
    const data = await res.json();
    if (Array.isArray(data) && Array.isArray(data[0])) {
      return data[0].map((item: [string, string]) => item[0]).join('');
    }
    return text;
  } catch {
    return text;
  }
}

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();
    const { paragraphs } = body as { paragraphs: string[] };

    if (!paragraphs || !Array.isArray(paragraphs)) {
      return new Response(JSON.stringify({ error: 'Array paragraphs diperlukan' }), { status: 400 });
    }

    // Terjemahkan per batch 5 paragraf paralel agar cepat dan tidak kena rate limit
    const translated: string[] = [];
    const batchSize = 5;

    for (let i = 0; i < paragraphs.length; i += batchSize) {
      const batch = paragraphs.slice(i, i + batchSize);
      const results = await Promise.all(batch.map((p) => translateChunk(p)));
      translated.push(...results);
    }

    return new Response(JSON.stringify({ translated }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Translation error';
    return new Response(JSON.stringify({ error: message }), { status: 500 });
  }
};
