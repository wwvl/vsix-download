<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import type { Extension } from '@/types/extension'
import { computed, h, resolveComponent, toRefs } from 'vue'
import { getDownloadUrl } from '@/composables/useExtension'

const props = defineProps<{
  extension: Extension
  visibleVersionCount?: number
}>()

const { extension } = toRefs(props)
const UButton = resolveComponent('UButton')
const UTooltip = resolveComponent('UTooltip')

interface VersionHistory {
  version: string
  lastUpdated: string
}

// 根据可见版本数量参数过滤版本历史数据
const filteredVersionHistory = computed(() => {
  if (!props.visibleVersionCount || props.visibleVersionCount <= 0) {
    return extension.value.version_history
  }
  return extension.value.version_history.slice(0, props.visibleVersionCount)
})

// 格式化日期
function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

// 定义表格列
const columns: TableColumn<VersionHistory>[] = [
  {
    accessorKey: 'version',
    header: '版本号',
    cell: ({ row }) => `v${row.getValue('version') as string}`,
  },
  {
    accessorKey: 'lastUpdated',
    header: '更新时间',
    cell: ({ row }) => formatDate(row.getValue('lastUpdated') as string),
  },
  {
    accessorKey: 'version',
    header: '下载',
    cell: ({ row }) => {
      const version = row.getValue('version') as string
      return h(
        UTooltip,
        {
          text: `下载 v${version}`,
        },
        () =>
          h(UButton, {
            size: 'xs',
            color: 'primary',
            icon: 'i-carbon-download',
            label: `${extension.value.extension_name}-${version}.vsix`,
            href: getDownloadUrl(extension.value.extension_name, version),
            target: '_blank',
            class: 'transition-transform hover:scale-110',
          }),
      )
    },
  },
]
</script>

<template>
  <div class="max-w-3xl">
    <div class="flex w-full flex-1 flex-col overflow-x-auto rounded-[calc(var(--ui-radius)*1.5)] border border-(--ui-border) focus:outline-hidden">
      <UTable
        :data="filteredVersionHistory"
        :columns="columns"
        :ui="{
          tr: 'transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/50',
          td: 'whitespace-nowrap',
        }"
      />
    </div>
  </div>
</template>
