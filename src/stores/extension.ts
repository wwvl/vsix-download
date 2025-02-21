import type { Extension } from '@/types/extension'
import { supabase } from '@/composables/useSupabase'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useExtensionStore = defineStore(
  'extension',
  () => {
    const extensions = ref<Extension[]>([])
    const loading = ref(false)
    const error = ref<Error | null>(null)

    function validateAndTransformExtension(data: any): Extension {
      if (!data.extension_name || !data.extension_id || !data.display_name) {
        throw new Error('Invalid extension data: missing required fields')
      }

      return {
        id: data.id,
        extension_id: data.extension_id,
        extension_name: data.extension_name,
        extension_full_name: data.extension_full_name,
        display_name: data.display_name,
        short_description: data.short_description,
        latest_version: data.latest_version || 'unknown',
        last_updated: data.last_updated,
        version_history: data.version_history || [],
        categories: data.categories || [],
        tags: data.tags || [],
        download_url: data.download_url,
        filename: data.filename,
        marketplace_url: data.marketplace_url,
      }
    }

    async function fetchExtensions() {
      loading.value = true
      error.value = null
      try {
        const { data, error: err } = await supabase.from('extensions').select('*').order('extension_full_name', { ascending: true })

        if (err) {
          console.error('Supabase error:', err)
          throw err
        }

        if (!data) {
          console.warn('No data returned from Supabase')
          extensions.value = []
          return
        }

        // 转换和验证数据
        const validExtensions = data
          .map((item) => {
            try {
              return validateAndTransformExtension(item)
            } catch (e) {
              console.error('Invalid extension data:', item, e)
              return null
            }
          })
          .filter((item): item is Extension => item !== null)

        console.error('Valid extensions count:', validExtensions.length)
        extensions.value = validExtensions
      } catch (err) {
        console.error('Error fetching extensions:', err)
        error.value = err as Error
      } finally {
        loading.value = false
      }
    }

    async function searchExtensions(query: string) {
      loading.value = true
      error.value = null
      try {
        const { data, error: err } = await supabase.from('extensions').select('*').textSearch('search_text', query)

        if (err) {
          console.error('Supabase search error:', err)
          throw err
        }

        if (!data) {
          console.warn('No search results returned from Supabase')
          extensions.value = []
          return
        }

        // 转换和验证搜索结果
        const validExtensions = data
          .map((item) => {
            try {
              return validateAndTransformExtension(item)
            } catch (e) {
              console.error('Invalid extension data in search results:', item, e)
              return null
            }
          })
          .filter((item): item is Extension => item !== null)

        console.error('Valid search results count:', validExtensions.length)
        extensions.value = validExtensions
      } catch (err) {
        console.error('Error searching extensions:', err)
        error.value = err as Error
      } finally {
        loading.value = false
      }
    }

    return {
      extensions,
      loading,
      error,
      fetchExtensions,
      searchExtensions,
    }
  },
  {
    persist: true,
  },
)
