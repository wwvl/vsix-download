<script setup lang="ts">
  import type { Extension } from '@/types/extension'
  import type { TableColumn } from '@nuxt/ui'
  import { useExtensionStore } from '@/stores/extension'
  import { onMounted } from 'vue'

  const store = useExtensionStore()

  onMounted(() => {
    store.fetchExtensions()
  })

  // 表格列定义
  const columns = [
    {
      key: 'extensionName',
      label: '扩展标识符',
      sortable: true,
    },
    {
      key: 'displayName',
      label: '显示名称',
      sortable: true,
    },
    {
      key: 'version',
      label: '版本号',
    },
    {
      key: 'lastUpdated',
      label: '更新日期',
      sortable: true,
    },
    {
      key: 'shortDescription',
      label: '描述',
    },
    {
      key: 'actions',
      label: '操作',
    },
  ] as const

  // 表格 UI 配置
  const tableUI = {
    root: 'relative overflow-auto',
    base: 'min-w-full table-fixed',
    td: 'whitespace-normal py-3 px-4',
    th: 'whitespace-nowrap py-3.5 px-4',
    empty: 'py-6 text-center text-sm text-gray-500',
    loading: {
      wrapper: 'absolute inset-0 flex items-center justify-center bg-gray-50 dark:bg-gray-800/50',
      icon: 'w-6 h-6 text-primary-500 animate-spin',
      label: 'ml-3 text-sm text-gray-500 dark:text-gray-400',
    },
  } as const
</script>

<template>
  <div class="min-h-screen p-4">
    <UContainer>
      <UCard class="mb-6">
        <template #header>
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold">扩展列表视图</h1>
              <p class="mt-2 text-gray-500">查看所有 VS Code 扩展的详细信息</p>
            </div>
            <div class="flex gap-4">
              <UInput v-model="store.searchQuery" icon="i-carbon-search" placeholder="搜索扩展..." class="w-64" />
              <USelect v-model="store.selectedCategories" :options="store.allCategories" multiple placeholder="选择分类" class="w-64" />
            </div>
          </div>
        </template>
      </UCard>

      <UAlert v-if="store.error" color="warning" variant="soft" icon="i-carbon-warning" title="加载失败" :description="store.error" class="mb-6" />

      <UTable :rows="store.filteredExtensions" :columns="columns" :loading="store.loading" loading-state="正在加载扩展数据..." :ui="tableUI">
        <!-- 扩展标识符列 -->
        <template #cell-extensionName="{ row }">
          <div class="flex items-center gap-2">
            <span class="font-mono text-sm">{{ (row as unknown as Extension).extensionName }}</span>
          </div>
        </template>

        <!-- 显示名称列 -->
        <template #cell-displayName="{ row }">
          <router-link :to="`/extension/${(row as unknown as Extension).extensionName}`" class="hover:text-primary-500 font-medium">
            {{ (row as unknown as Extension).displayName }}
          </router-link>
        </template>

        <!-- 版本号列 -->
        <template #cell-version="{ row }">
          <UBadge color="neutral" variant="soft" size="sm">
            {{ (row as unknown as Extension).latest_version.version }}
          </UBadge>
        </template>

        <!-- 更新日期列 -->
        <template #cell-lastUpdated="{ row }">
          <div class="flex items-center gap-1 text-gray-500">
            <UIcon name="i-carbon-time" class="size-4" />
            <span>{{ new Date((row as unknown as Extension).latest_version.lastUpdated).toLocaleDateString('zh-CN') }}</span>
          </div>
        </template>

        <!-- 描述列 -->
        <template #cell-shortDescription="{ row }">
          <p class="line-clamp-2 text-sm text-gray-500">
            {{ (row as unknown as Extension).shortDescription }}
          </p>
        </template>

        <!-- 操作列 -->
        <template #cell-actions="{ row }">
          <div class="flex items-center gap-2">
            <UButton :to="(row as unknown as Extension).marketplaceUrl" target="_blank" color="primary" variant="soft" size="xs" icon="i-carbon-launch"> 查看 </UButton>
          </div>
        </template>
      </UTable>

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
          :to="(page) => ({ query: { page } })"
          :ui="{
            root: 'flex items-center gap-2',
            list: 'flex items-center gap-1',
          }"
        />
      </div>
    </UContainer>
  </div>
</template>
