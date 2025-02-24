<script setup lang="ts">
import type { Extension } from '@/types/extension'
import type { TableColumn } from '@nuxt/ui'
import { h, resolveComponent, toRefs } from 'vue'

const props = defineProps<{
  extension: Extension
}>()

const { extension } = toRefs(props)
const UButton = resolveComponent('UButton')
const UTooltip = resolveComponent('UTooltip')

interface VersionHistory {
  version: string
  lastUpdated: string
}

function getDownloadUrl(extensionName: string, version: string): string {
  const [publisher, name] = extensionName.split('.')
  return `https://marketplace.visualstudio.com/_apis/public/gallery/publishers/${publisher}/vsextensions/${name}/${version}/vspackage`
}

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
        :data="extension.version_history"
        :columns="columns"
        :ui="{
          tr: 'transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/50',
          td: 'whitespace-nowrap',
        }"
      />
    </div>
  </div>
</template>
