import { createClient, type SupabaseClient } from '@supabase/supabase-js';

export interface Novel {
  id: string;
  slug: string;
  title: string;
  author: string;
  cover_url: string;
  total_chapters: number;
  description?: string;
  created_at?: string;
}

export interface Chapter {
  id: string;
  novel_slug: string;
  chapter_number: number;
  chapter_index: number;
  title: string;
  r2_key: string;
}

const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.PUBLIC_SUPABASE_ANON_KEY || '';

export const isSupabaseConfigured = Boolean(
  supabaseUrl && supabaseAnonKey && !supabaseUrl.includes('your-project')
);

export const supabase: SupabaseClient | null = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;
