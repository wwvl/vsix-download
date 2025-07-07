<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'
import type { Column } from '@tanstack/vue-table'
import type { Extension } from '@/types/extension'

import { getPaginationRowModel } from '@tanstack/vue-table'
import { useEventListener } from '@vueuse/core'
import { upperFirst } from 'scule'
import { computed, h, ref, resolveComponent, toRefs } from 'vue'
import { useRouter } from 'vue-router'
import { useExtension } from '@/composables/useExtension'

const props = defineProps<{
  extensions: Extension[]
  loading?: boolean
  error?: Error | null
}>()

const emit = defineEmits<{
  (e: 'update:selectedExtensions', extensions: Extension[]): void
  (e: 'copyExtensions', extensionIds: string[]): void
}>()

const { extensions } = toRefs(props)

const router = useRouter()
const toast = useToast()
const { copyExtensionIds } = useExtension()
const UButton = resolveComponent('UButton')
const UCheckbox = resolveComponent('UCheckbox')

// 搜索输入框引用
const searchInput = ref<HTMLInputElement | null>(null)

// 行选择状态
const rowSelection = ref({})
const expanded = ref({})

// 排序状态
const sorting = ref([
  {
    id: 'last_updated',
    desc: true,
  },
])

// 分页状态
const pagination = ref({
  pageIndex: 0,
  pageSize: 25,
})

// 页面大小选项
const pageSizeOptions = ref([
  { label: '25 条/页', value: 25 },
  { label: '50 条/页', value: 50 },
  { label: '75 条/页', value: 75 },
  { label: '100 条/页', value: 100 },
])

// 全局搜索状态
const globalFilter = ref('')

// 快捷键监听
useEventListener(document, 'keydown', (e) => {
  if (e.key === 'Escape' && document.activeElement?.tagName === 'INPUT') {
    globalFilter.value = ''
    return
  }

  if (e.key === 'k' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    searchInput.value?.focus()
  }
})

// 表格实例
const table = ref<any>(null)

// 当前页码状态
const currentPage = computed({
  get: () => (table.value?.tableApi?.getState().pagination.pageIndex || 0) + 1,
  set: (page: number) => table.value?.tableApi?.setPageIndex(page - 1),
})

// 列可见性状态
const columnVisibility = ref({
  extension_name: true,
  display_name: true,
  latest_version: true,
  last_updated: true,
  categories: true,
  tags: true,
  actions: true,
})

interface ColumnType {
  id: string
  getIsVisible: () => boolean
  getCanHide: () => boolean
}

// 列定义
const columns: TableColumn<Extension>[] = [
  {
    id: 'select',
    header: ({ table }) =>
      h(UCheckbox, {
        'modelValue': table.getIsSomePageRowsSelected() ? 'indeterminate' : table.getIsAllPageRowsSelected(),
        'onUpdate:modelValue': (value: boolean | 'indeterminate') => table.toggleAllPageRowsSelected(!!value),
        'ariaLabel': '选择全部',
      }),
    cell: ({ row }) =>
      h(UCheckbox, {
        'modelValue': row.getIsSelected(),
        'onUpdate:modelValue': (value: boolean | 'indeterminate') => row.toggleSelected(!!value),
        'ariaLabel': '选择行',
      }),
  },
  {
    id: 'expand',
    cell: ({ row }) =>
      h(UButton, {
        color: 'neutral',
        variant: 'ghost',
        icon: 'i-carbon-chevron-down',
        square: true,
        ui: {
          leadingIcon: ['transition-transform', row.getIsExpanded() ? 'duration-200 rotate-180' : ''],
        },
        onClick: () => row.toggleExpanded(),
      }),
  },
  {
    accessorKey: 'extension_name',
    header: ({ column }) => getHeader(column, '扩展 ID'),
    enableSorting: true,
  },
  {
    accessorKey: 'display_name',
    header: ({ column }) => getHeader(column, '扩展名称'),
    enableSorting: true,
  },
  {
    accessorKey: 'latest_version',
    header: ({ column }) => getHeader(column, '最新版本'),
    enableSorting: true,
  },
  {
    accessorKey: 'last_updated',
    header: ({ column }) => getHeader(column, '更新时间'),
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
    header: '操作',
  },
]

// 从列定义中生成列名映射
const columnLabels = computed(() => {
  const labels: Record<string, string> = {
    extension_name: '扩展 ID',
    display_name: '扩展名称',
    latest_version: '最新版本',
    last_updated: '更新时间',
    categories: '分类',
    tags: '标签',
    actions: '操作',
  }
  return Object.fromEntries(columns.filter(col => (col as any).accessorKey).map(col => [(col as any).accessorKey, labels[(col as any).accessorKey] || upperFirst((col as any).accessorKey)]))
})

// 获取表头组件
function getHeader(column: Column<Extension>, label: string) {
  const isSorted = column.getIsSorted()

  return h(UButton, {
    color: 'neutral',
    variant: 'ghost',
    label,
    icon:
        isSorted
          ? isSorted === 'asc'
            ? 'i-carbon-arrow-up'
            : 'i-carbon-arrow-down'
          : 'i-carbon-arrows-vertical',
    class: '-mx-2.5',
    onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
  })
}

// 复制选中行的扩展 ID
async function copySelectedCommands() {
  const selectedRows = table.value?.tableApi?.getSelectedRowModel().rows || []
  if (selectedRows.length === 0) {
    toast.add({
      title: '请先选择要复制的扩展',
      color: 'warning',
      icon: 'i-carbon-warning-alt',
    })
    return
  }

  const extensionIds = selectedRows.map((row: any) => row.original.extension_name)
  await copyExtensionIds(extensionIds)
  emit('copyExtensions', extensionIds)
}

// 跳转到扩展详情页
function navigateToExtension(extensionName: string): void {
  router.push(`/extension/${extensionName}`)
}
</script>

<template>
  <div class="space-y-4 md:space-y-6">
    <UAlert
      :title="`当前共有 ${extensions.length} 个 VSCode 扩展`"
      color="primary"
      variant="subtle"
      icon="i-carbon-data-vis-1"
      class="mx-2 transform shadow-sm transition-all duration-300 hover:scale-[1.01] sm:mx-0"
    />

    <div class="mx-auto w-full max-w-4xl px-4">
      <UInput
        ref="searchInput"
        v-model="globalFilter"
        name="queryInput"
        placeholder="搜索扩展..."
        icon="i-carbon-search"
        size="xl"
        color="primary"
        variant="outline"
        class="w-full shadow-sm transition-shadow duration-200 hover:shadow"
      >
        <template #trailing>
          <UKbd>Ctrl</UKbd>
          <UKbd>K</UKbd>
        </template>
      </UInput>
    </div>

    <div class="flex w-full flex-1 flex-col overflow-x-auto rounded-[calc(var(--ui-radius)*1.5)] border border-(--ui-border) focus:outline-hidden">
      <div class="grid grid-cols-1 items-center gap-2 border-b border-(--ui-border-accented) px-4 py-3.5 md:grid-cols-2 md:gap-4 lg:grid-cols-3">
        <div class="flex w-full items-center justify-center gap-2 md:justify-start md:gap-4">
          <UButton
            :disabled="table?.tableApi?.getFilteredSelectedRowModel().rows.length === 0"
            color="neutral"
            variant="outline"
            icon="i-carbon-copy"
            class="transform text-sm whitespace-nowrap transition-all duration-300 hover:scale-[1.02] md:text-base"
            @click="copySelectedCommands"
          >
            复制 ID
          </UButton>
        </div>

        <div class="mt-2 flex items-center justify-center md:mt-0">
          <UPagination v-model:page="currentPage" :items-per-page="table?.tableApi?.getState().pagination.pageSize" :total="table?.tableApi?.getFilteredRowModel().rows.length" />
        </div>

        <div class="mt-2 flex items-center justify-center md:mt-0 md:justify-end">
          <UDropdownMenu
            :items="
              table?.tableApi
                ?.getAllColumns()
                .filter((column: ColumnType) => column.getCanHide())
                .map((column: ColumnType) => ({
                  label: columnLabels[column.id] || upperFirst(column.id),
                  type: 'checkbox',
                  checked: column.getIsVisible(),
                  onUpdateChecked(checked: boolean) {
                    table?.tableApi?.getColumn(column.id)?.toggleVisibility(!!checked)
                  },
                  onSelect(e?: Event) {
                    e?.preventDefault()
                  },
                }))
            "
            :content="{ align: 'end' }"
          >
            <UButton
              label="显示列"
              color="neutral"
              variant="outline"
              trailing-icon="i-carbon-chevron-down"
              class="w-full transform text-sm shadow-sm transition-all duration-300 hover:scale-[1.02] md:w-auto md:text-base"
            />
          </UDropdownMenu>
        </div>
      </div>

      <UTable
        ref="table"
        v-model:expanded="expanded"
        v-model:column-visibility="columnVisibility"
        v-model:row-selection="rowSelection"
        v-model:sorting="sorting"
        v-model:pagination="pagination"
        v-model:global-filter="globalFilter"
        sticky
        :data="extensions"
        :columns="columns"
        :loading="loading"
        :pagination-options="{
          getPaginationRowModel: getPaginationRowModel(),
        }"
        :ui="{
          base: 'min-w-full overflow-x-auto',
          tr: 'transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/50 data-[expanded=true]:bg-gray-100/50 dark:data-[expanded=true]:bg-gray-800/50',
          td: 'whitespace-normal break-words text-sm md:text-base p-2 md:p-4',
          th: 'whitespace-normal break-words text-sm md:text-base p-2 md:p-4',
        }"
        class="w-full"
      >
        <template #expanded="{ row }">
          <ExtensionExpandedContent :extension="row.original" />
        </template>

        <template #extension_name-cell="{ row }">
          <div
            class="group hover:text-primary-500 flex max-w-full cursor-pointer items-center gap-1 text-sm leading-relaxed break-words whitespace-normal transition-colors duration-300 md:max-w-[266px] md:gap-2 md:text-base"
            role="link"
            @click="navigateToExtension(row.original.extension_name)"
          >
            <span class="group-hover:underline">{{ row.original.extension_name }}</span>
            <UButton
              icon="i-carbon-copy"
              color="primary"
              variant="ghost"
              size="xs"
              class="transform transition-all duration-300 hover:scale-110"
              @click.stop="copyExtensionIds([row.original.extension_name])"
            />
          </div>
        </template>

        <template #display_name-cell="{ row }">
          <UButton
            :href="row.original.marketplace_url"
            target="_blank"
            color="neutral"
            variant="link"
            class="hover:text-primary-500 !p-0 text-sm leading-relaxed break-words whitespace-normal transition-colors duration-300 md:text-base"
          >
            {{ row.original.display_name }}
          </UButton>
        </template>

        <template #categories-cell="{ row }">
          <div class="flex flex-wrap gap-1 md:gap-1.5">
            <UBadge
              v-for="category in row.original.categories"
              :key="category"
              :label="category"
              color="secondary"
              variant="subtle"
              size="sm"
              class="transform text-xs transition-all duration-300 hover:scale-105 md:text-sm"
            />
          </div>
        </template>

        <template #tags-cell="{ row }">
          <div class="flex flex-wrap gap-1 md:gap-1.5">
            <UBadge
              v-for="tag in row.original.tags"
              :key="tag"
              :label="tag"
              color="secondary"
              variant="subtle"
              size="xs"
              class="transform text-xs transition-all duration-300 hover:scale-105 md:text-sm"
            />
          </div>
        </template>

        <template #last_updated-cell="{ row }">
          <span class="text-xs text-gray-600 md:text-sm dark:text-gray-300">
            {{ new Date(row.original.last_updated).toLocaleString() }}
          </span>
        </template>

        <template #actions-cell="{ row }">
          <ExtensionActions :extension="row.original" />
        </template>
      </UTable>

      <div class="flex flex-col items-center justify-between gap-4 border-t border-(--ui-border-accented) px-4 py-3.5 text-xs md:flex-row md:gap-4 md:text-sm">
        <div class="w-full text-center md:w-auto md:text-left">
          已选择 {{ table?.tableApi?.getFilteredSelectedRowModel().rows.length || 0 }} / {{ table?.tableApi?.getFilteredRowModel().rows.length || 0 }} 行
        </div>
        <div class="flex w-full flex-col items-center gap-4 md:w-auto md:flex-row md:items-center md:justify-end">
          <USelect
            v-model="pagination.pageSize"
            :items="pageSizeOptions"
            placeholder="每页显示数量"
            :ui="{
              trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200',
            }"
            class="w-full max-w-[200px] md:w-36"
          />
          <div class="flex w-full justify-center md:w-auto">
            <UPagination v-model:page="currentPage" :items-per-page="table?.tableApi?.getState().pagination.pageSize" :total="table?.tableApi?.getFilteredRowModel().rows.length" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
