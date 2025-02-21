<script setup lang="ts">
  import type { Extension } from '@/types/extension'
  import type { DropdownMenuItem, TableColumn } from '@nuxt/ui'
  import { useExtensionStore } from '@/stores/extension'
  import { computed, h, onMounted } from 'vue'

  const store = useExtensionStore()
  const toast = useToast()

  // 添加计算属性来监控数据变化
  const extensionsCount = computed(() => store.extensions?.length || 0)

  const columns: TableColumn<Extension>[] = [
    {
      accessorKey: 'extension_full_name',
      header: '扩展名称',
    },
    {
      accessorKey: 'display_name',
      header: '显示名称',
    },
    {
      accessorKey: 'latest_version',
      header: '最新版本',
    },
    {
      accessorKey: 'last_updated',
      header: '更新时间',
      enableSorting: true,
    },
    {
      accessorKey: 'categories',
      header: '分类',
    },
    {
      accessorKey: 'tags',
      header: '标签',
    },
    {
      accessorKey: 'actions',
      header: '',
    },
  ]

  function getDropdownActions(extension: Extension): DropdownMenuItem[][] {
    return [
      [
        {
          label: '复制扩展 ID',
          icon: 'i-lucide-copy',
          onSelect: () => {
            navigator.clipboard.writeText(extension.extension_id)
            toast.add({
              title: '扩展 ID 已复制到剪贴板！',
              color: 'success',
              icon: 'i-lucide-circle-check',
            })
          },
        },
      ],
      [
        {
          label: '下载',
          icon: 'i-lucide-download',
          onSelect: () => {
            window.open(extension.download_url, '_blank')
          },
        },
        {
          label: '查看详情',
          icon: 'i-lucide-external-link',
          onSelect: () => {
            window.open(extension.marketplace_url, '_blank')
          },
        },
      ],
    ]
  }

  onMounted(async () => {
    try {
      await store.fetchExtensions()
    } catch (err) {
      console.error('Failed to fetch extensions:', err)
    }
  })
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div v-if="store.loading" class="text-center">
      <USkeleton class="mx-auto h-8 w-full max-w-sm" />
      <USkeleton class="mt-4 h-32 w-full" />
      <USkeleton class="mt-4 h-32 w-full" />
    </div>
    <div v-else-if="store.error" class="text-center">
      <UAlert :title="store.error.message" color="error" variant="soft" icon="i-carbon-warning-alt" />
    </div>
    <div v-else>
      <UAlert :title="`当前共有 ${extensionsCount} 个 VSCode 扩展`" color="primary" variant="subtle" icon="i-carbon-application-web" class="mb-4" />

      <UTable :data="store.extensions" :columns="columns" :loading="store.loading" :sort="{ column: 'last_updated', direction: 'desc' }" class="w-full">
        <template #extension_name-cell="{ row }">
          <div class="flex items-center gap-3">
            <div class="font-medium text-gray-900">
              {{ row.original.extension_name }}
            </div>
          </div>
        </template>

        <template #categories-cell="{ row }">
          <div class="flex flex-wrap gap-1">
            <UBadge v-for="category in row.original.categories" :key="category" :label="category" color="primary" variant="subtle" size="sm" />
          </div>
        </template>

        <template #tags-cell="{ row }">
          <div class="flex flex-wrap gap-1">
            <UBadge v-for="tag in row.original.tags" :key="tag" :label="tag" color="neutral" variant="subtle" size="xs" />
          </div>
        </template>

        <template #last_updated-cell="{ row }">
          {{ new Date(row.original.last_updated).toLocaleString() }}
        </template>

        <template #actions-cell="{ row }">
          <div class="flex justify-end">
            <UDropdownMenu :items="getDropdownActions(row.original)">
              <UButton icon="i-lucide-ellipsis-vertical" color="neutral" variant="ghost" />
            </UDropdownMenu>
          </div>
        </template>
      </UTable>
    </div>
  </div>
</template>
