import type { Novel, Chapter } from './supabase';

export const INITIAL_NOVELS: Novel[] = [
  {
    id: 'myst-might-mayhem',
    slug: 'myst-might-mayhem',
    title: 'Myst, Might, Mayhem',
    author: 'Midwinter Moonlight (한중월야)',
    cover_url: 'https://images.novelping.com/novel/myst-might-mayhem.jpg',
    total_chapters: 526,
    description: 'Kisah Mok Gyeong-un yang bangkit dari jurang keputusasaan di dunia persilatan Murim dengan kegelapan, misteri, dan kekuatan mutlak.',
  },
  {
    id: 'the-heavenly-demon-cant-live-a-normal-life',
    slug: 'the-heavenly-demon-cant-live-a-normal-life',
    title: "The Heavenly Demon Can't Live a Normal Life",
    author: 'Sancheon',
    cover_url: 'https://images.novelping.com/novel/the-heavenly-demon-cant-live-a-normal-life.jpg',
    total_chapters: 612,
    description: 'Baek Joong-hyuk, sang Iblis Surgawi terhebat di benua Murim, bereinkarnasi ke dalam tubuh Roman Dmitry, putra tertua keluarga Dmitry di dunia fantasi Barat.',
  },
  {
    id: 'star-embracing-swordmaster',
    slug: 'star-embracing-swordmaster',
    title: 'Star Embracing Swordmaster',
    author: 'Q10',
    cover_url: 'https://images.novelping.com/novel/star-embracing-swordmaster.jpg',
    total_chapters: 258,
    description: 'Vlad, seorang pemuda jalanan kumuh yang memegang pedang dengan tatapan teguh mengarah ke langit berbintang, menempuh takdir kesatria sejati.',
  },
];

export function getLocalNovel(slug: string): Novel | undefined {
  return INITIAL_NOVELS.find((n) => n.slug === slug);
}
