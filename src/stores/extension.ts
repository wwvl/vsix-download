import type { Extension } from '@/types/extension'
import { supabase } from '@/composables/useSupabase'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useExtensionStore = defineStore(
  'extension',
  () => {
    // 基础状态
    const extensions = ref<Extension[]>([])
    const loading = ref(false)
    const error = ref<Error | null>(null)

    // 数据验证和转换
    function validateAndTransformExtension(data: any): Extension {
      if (!data.extension_name || !data.display_name) {
        throw new Error('Invalid extension data: missing required fields')
      }

      return {
        extension_name: data.extension_name,
        display_name: data.display_name,
        short_description: data.short_description,
        latest_version: data.latest_version || 'unknown',
        last_updated: data.last_updated,
        version_history: data.version_history || [],
        categories: data.categories || [],
        tags: data.tags || [],
        download_url: data.download_url,
        marketplace_url: data.marketplace_url,
      }
    }

    // 获取扩展列表
    async function fetchExtensions() {
      loading.value = true
      error.value = null
      try {
        const { data, error: err } = await supabase.from('extensions').select('*').order('last_updated', { ascending: false })

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

        extensions.value = validExtensions
      } catch (err) {
        console.error('Error fetching extensions:', err)
        error.value = err as Error
      } finally {
        loading.value = false
      }
    }

    return {
      // 状态
      extensions,
      loading,
      error,

      // 方法
      fetchExtensions,
    }
  },
  {
    persist: true,
  },
)
