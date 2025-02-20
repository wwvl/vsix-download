import type { Extension } from '@/types/extension'
import { defineStore } from 'pinia'

export const useExtensionStore = defineStore('extension', {
  state: () => ({
    extensions: [] as Extension[],
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
      try {
        const response = await fetch('/data/extensions.json')
        const data = await response.json()
        this.extensions = data
      } catch (error) {
        console.error('Failed to fetch extensions:', error)
      }
    },
  },
})
