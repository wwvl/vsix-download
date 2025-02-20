import type { Extension } from '@/types/extension'
import { computed, ref } from 'vue'

export function useExtensionSearch(extensions: Extension[]) {
  const searchQuery = ref('')
  const selectedCategories = ref<string[]>([])

  const filteredExtensions = computed(() => {
    return extensions.filter((ext) => {
      const matchesSearch =
        !searchQuery.value || ext.displayName.toLowerCase().includes(searchQuery.value.toLowerCase()) || ext.shortDescription.toLowerCase().includes(searchQuery.value.toLowerCase())

      const matchesCategories = !selectedCategories.value.length || ext.categories.some((cat) => selectedCategories.value.includes(cat))

      return matchesSearch && matchesCategories
    })
  })

  return {
    searchQuery,
    selectedCategories,
    filteredExtensions,
  }
}
