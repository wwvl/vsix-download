import type { Extension } from '@/types/extension'
// composables/useExtensions.ts
import { ref } from 'vue'

export function useExtensions() {
  const extensions = ref<Extension[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const fetchExtensions = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch('/data/extensions.json')
      extensions.value = await response.json()
    }
    catch (e) {
      error.value = e as Error
    }
    finally {
      loading.value = false
    }
  }

  return {
    extensions,
    loading,
    error,
    fetchExtensions,
  }
}
