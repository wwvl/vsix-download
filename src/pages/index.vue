<script setup lang="ts">
  import { useExtensionStore } from '@/stores/extension'
  import { onMounted, watch } from 'vue'
  import { useRoute } from 'vue-router'

  const route = useRoute()
  const store = useExtensionStore()

  // 监听路由参数变化
  watch(
    () => route.query.page,
    (newPage) => {
      const page = Number(newPage) || 1
      if (page !== store.currentPage) {
        store.currentPage = page
      }
    },
    { immediate: true },
  )

  onMounted(() => {
    store.fetchExtensions()
  })

  // 分页链接处理函数
  function paginationTo(page: number) {
    return {
      query: { page },
      // hash: '#extensions',
    }
  }
</script>

<template>
  <div class="min-h-screen p-4">
    <UContainer>
      <UCard class="mb-6">
        <template #header>
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold">VS Code 扩展市场</h1>
              <p class="mt-2 text-gray-500">浏览和搜索 Visual Studio Code 扩展</p>
            </div>
            <div class="flex items-center gap-4">
              <UInput v-model="store.searchQuery" icon="i-carbon-search" placeholder="搜索扩展..." class="w-64" />
              <USelect v-model="store.selectedCategories" :options="store.allCategories" multiple placeholder="选择分类" class="w-64" />
            </div>
          </div>
        </template>
      </UCard>

      <UAlert v-if="store.error" color="warning" variant="soft" icon="i-carbon-warning" title="加载失败" :description="store.error" class="mb-6" />

      <div v-if="store.loading" class="flex justify-center py-8">
        <ULoading />
      </div>

      <template v-else-if="!store.error">
        <div id="extensions" class="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          <ExtensionCard v-for="extension in store.paginatedExtensions" :key="extension.extensionId" :extension="extension" />
        </div>

        <div class="mt-6 flex justify-center">
          <UPagination
            v-if="store.totalPages > 1"
            v-model="store.currentPage"
            :total="store.filteredExtensions.length"
            :items-per-page="store.pageSize"
            :sibling-count="2"
            show-edges
            color="primary"
            variant="soft"
            active-color="primary"
            active-variant="solid"
            size="md"
            :to="paginationTo"
            :ui="{
              root: 'flex items-center gap-2',
              list: 'flex items-center gap-1',
            }"
          />
        </div>
      </template>
    </UContainer>
  </div>
</template>
