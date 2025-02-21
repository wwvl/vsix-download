import { createClient } from '@supabase/supabase-js'
import { ref } from 'vue'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY

if (!supabaseUrl || !supabaseKey) {
  throw new Error('请在 .env 文件中设置 VITE_SUPABASE_URL 和 VITE_SUPABASE_KEY')
}

export const supabase = createClient(supabaseUrl, supabaseKey)

export function useSupabase() {
  const loading = ref(false)
  const error = ref<Error | null>(null)

  return {
    supabase,
    loading,
    error,
  }
}
