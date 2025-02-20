<script setup lang="ts">
  import { useExtensionStore } from '@/stores/extension'
  import { onMounted } from 'vue'

  const store = useExtensionStore()

  onMounted(() => {
    store.fetchExtensions()
  })
</script>

<template>
  <div class="min-h-screen p-4">
    <UContainer>
      <UPageHeader title="VS Code 扩展市场" description="浏览和搜索 Visual Studio Code 扩展">
        <template #right>
          <div class="flex gap-4">
            <UInput v-model="store.searchQuery" icon="i-heroicons-magnifying-glass" placeholder="搜索扩展..." class="w-64" />
            <USelect v-model="store.selectedCategories" :options="store.allCategories" multiple placeholder="选择分类" class="w-64" />
          </div>
        </template>
      </UPageHeader>

      <div class="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        <ExtensionCard v-for="extension in store.paginatedExtensions" :key="extension.extensionId" :extension="extension" />
      </div>

      <div class="mt-6 flex justify-center">
        <UPagination v-model="store.currentPage" :total="store.totalPages" :ui="{ rounded: 'rounded-full' }" />
      </div>
    </UContainer>
  </div>
</template>
