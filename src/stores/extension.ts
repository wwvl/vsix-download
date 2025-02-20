import type { Extension } from '@/types/extension'
import { defineStore } from 'pinia'

export const useExtensionStore = defineStore('extension', {
  state: () => ({
    extensions: [] as Extension[],
    loading: false,
    error: null as string | null,
    searchQuery: '',
    selectedCategories: [] as string[],
    currentPage: 1,
    pageSize: 12,
  }),

  getters: {
    allCategories(): string[] {
      const categories = new Set<string>()
      this.extensions.forEach((ext) => ext.categories.forEach((cat) => categories.add(cat)))
      return Array.from(categories).sort()
    },

    filteredExtensions(): Extension[] {
      return this.extensions.filter((ext) => {
        const matchesSearch = !this.searchQuery || ext.displayName.toLowerCase().includes(this.searchQuery.toLowerCase()) || ext.shortDescription.toLowerCase().includes(this.searchQuery.toLowerCase())

        const matchesCategories = !this.selectedCategories.length || ext.categories.some((cat) => this.selectedCategories.includes(cat))

        return matchesSearch && matchesCategories
      })
    },

    paginatedExtensions(): Extension[] {
      const start = (this.currentPage - 1) * this.pageSize
      return this.filteredExtensions.slice(start, start + this.pageSize)
    },

    totalPages(): number {
      return Math.ceil(this.filteredExtensions.length / this.pageSize)
    },
  },

  actions: {
    async fetchExtensions() {
      this.loading = true
      this.error = null

      try {
        const modules = import.meta.glob<{ default: Extension }>('../data/*.json')
        const results = await Promise.all(
          Object.entries(modules).map(async ([_path, loader]) => {
            const module = await loader()
            return module.default
          }),
        )

        this.extensions = results.filter(Boolean)
      } catch (error) {
        console.error('Failed to fetch extensions:', error)
        this.error = error instanceof Error ? error.message : '加载扩展数据失败'
      } finally {
        this.loading = false
      }
    },
  },
})
