import type { Extension } from '@/types/extension'
import { computed } from 'vue'

export function useExtensionCategories(extensions: Extension[]) {
  const categories = computed(() => {
    const categorySet = new Set<string>()
    extensions.forEach((ext) => {
      ext.categories.forEach(cat => categorySet.add(cat))
    })
    return Array.from(categorySet).sort()
  })

  return {
    categories,
  }
}
