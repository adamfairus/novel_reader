import type { APIRoute } from 'astro';
import { INITIAL_NOVELS } from '../../lib/novels';
import { supabase, isSupabaseConfigured } from '../../lib/supabase';

export const GET: APIRoute = async () => {
  if (isSupabaseConfigured && supabase) {
    try {
      const { data, error } = await supabase.from('novels').select('*').order('created_at', { ascending: false });
      if (!error && data && data.length > 0) {
        return new Response(JSON.stringify(data), {
          headers: { 'Content-Type': 'application/json' },
        });
      }
    } catch {
      // fallback to initial
    }
  }

  return new Response(JSON.stringify(INITIAL_NOVELS), {
    headers: { 'Content-Type': 'application/json' },
  });
};
