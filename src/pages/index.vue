<script setup lang="ts">
import type { Extension } from '@/types/extension'
import type { TableColumn } from '@nuxt/ui'
import type { Column } from '@tanstack/vue-table'

import { useExtension } from '@/composables/useExtension'
import { useExtensionStore } from '@/stores/extension'
import { getPaginationRowModel } from '@tanstack/vue-table'
import { useEventListener } from '@vueuse/core'
import { upperFirst } from 'scule'
import { computed, h, onMounted, ref, resolveComponent, useTemplateRef, watch } from 'vue'
import { useRouter } from 'vue-router'

const store = useExtensionStore()
const router = useRouter()
const toast = useToast()
const { copyExtensionIds } = useExtension()
const UButton = resolveComponent('UButton')
const UCheckbox = resolveComponent('UCheckbox')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UPagination = resolveComponent('UPagination')
const UInput = resolveComponent('UInput')
const UKbd = resolveComponent('UKbd')

// 添加搜索输入框引用
const searchInput = ref<HTMLInputElement | null>(null)

// 添加行选择状态
const rowSelection = ref({})
const expanded = ref({})
const selectedRows = ref<Extension[]>([])

// 添加排序状态
const sorting = ref([
  {
    id: 'last_updated',
    desc: true,
  },
])

// 添加分页状态
const pagination = ref({
  pageIndex: 0,
  pageSize: 36,
})

// 添加页面大小选项
const pageSizeOptions = ref([
  { label: '20 条/页', value: 20 },
  { label: '36 条/页', value: 36 },
  { label: '50 条/页', value: 50 },
  { label: '100 条/页', value: 100 },
])

// 添加全局搜索状态
const globalFilter = ref('')

// 添加快捷键监听
useEventListener(document, 'keydown', (e) => {
  // 如果当前焦点在输入框中，且按下了 Escape 键
  if (e.key === 'Escape' && document.activeElement?.tagName === 'INPUT') {
    globalFilter.value = ''
    return
  }

  // 如果按下了 Ctrl + K
  if (e.key === 'k' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault() // 阻止默认行为
    searchInput.value?.focus()
  }
})

interface TableColumnDef {
  id: string
  getCanHide: () => boolean
  getIsVisible: () => boolean
}

interface TableApi {
  getAllColumns: () => TableColumnDef[]
  getColumn: (id: string) => { toggleVisibility: (visible: boolean) => void } | undefined
  getFilteredSelectedRowModel: () => { rows: Extension[] }
  getFilteredRowModel: () => { rows: Extension[] }
  getIsSomePageRowsSelected: () => boolean
  getIsAllPageRowsSelected: () => boolean
  toggleAllPageRowsSelected: (value: boolean) => void
  toggleAllRowsSelected: (value: boolean) => void
  getSelectedRowModel: () => { rows: Extension[] }
  getState: () => {
    pagination: {
      pageIndex: number
      pageSize: number
    }
  }
  setPageIndex: (index: number) => void
}

interface TableInstance {
  tableApi: TableApi
}

const table = ref<TableInstance | null>(null)

// 添加当前页码状态
const currentPage = computed({
  get: () => (table.value?.tableApi?.getState().pagination.pageIndex || 0) + 1,
  set: (page: number) => table.value?.tableApi?.setPageIndex(page - 1),
})

// 监听页面大小变化
watch(
  () => pagination.value.pageSize,
  (_newPageSize) => {
    // 重置到第一页
    pagination.value.pageIndex = 0
    // 更新当前页码
    currentPage.value = 1
  },
)

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
}

// 添加计算属性来监控数据变化
const extensionsCount = computed(() => store.extensions?.length || 0)

// 添加列可见性状态
const columnVisibility = ref({
  extension_name: true,
  display_name: true,
  latest_version: true,
  last_updated: true,
  categories: true,
  tags: true,
  actions: true,
})

// 监听选择状态变化
watch(
  rowSelection,
  (newValue) => {
    if (Object.keys(newValue).length) {
      // 更新选中状态
      selectedRows.value = table.value?.tableApi?.getSelectedRowModel().rows || []
    }
  },
  { deep: true },
)

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

// 添加 UI 配置
const ui = {
  container: 'container mx-auto px-4 py-8 md:py-6 sm:py-4 transition-all duration-300 min-h-screen',
  loadingWrapper: 'space-y-4 text-center',
  errorAlert: 'transform text-center transition-transform duration-300 hover:scale-[1.02]',
  statsAlert: 'transform shadow-sm transition-all duration-300 hover:scale-[1.01] mx-2 sm:mx-0',
  tableWrapper: 'flex w-full flex-1 flex-col rounded-[calc(var(--ui-radius)*1.5)] border border-(--ui-border) focus:outline-hidden overflow-x-auto',
  tableHeader: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 items-center gap-4 border-b border-(--ui-border-accented) px-4 py-3.5',
  headerLeft: 'flex items-center justify-center md:justify-start gap-2 md:gap-4 w-full',
  headerCenter: 'flex items-center justify-center mt-4 md:mt-0',
  headerRight: 'flex items-center justify-center md:justify-end mt-4 md:mt-0',
  copyButton: 'transform transition-all duration-300 hover:scale-[1.02] text-sm md:text-base whitespace-nowrap',
  searchInput: 'flex-1 min-w-0',
  columnButton: 'transform shadow-sm transition-all duration-300 hover:scale-[1.02] text-sm md:text-base w-full md:w-auto',
  extensionId:
      'hover:text-primary-500 flex max-w-full md:max-w-[266px] cursor-pointer items-center gap-1 md:gap-2 leading-relaxed break-words whitespace-normal transition-colors duration-300 text-sm md:text-base',
  extensionName: 'hover:text-primary-500 !p-0 leading-relaxed break-words whitespace-normal transition-colors duration-300 text-sm md:text-base',
  badgeWrapper: 'flex flex-wrap gap-1 md:gap-1.5',
  badge: 'transform transition-all duration-300 hover:scale-105 text-xs md:text-sm',
  dateText: 'text-xs md:text-sm text-gray-600 dark:text-gray-300',
  actionButton: 'transform transition-all duration-300 hover:scale-110',
  tableFooter: 'flex flex-col md:flex-row items-center justify-between gap-2 md:gap-4 border-t border-(--ui-border-accented) px-4 py-3.5 text-xs md:text-sm',
  table: {
    base: 'min-w-full overflow-x-auto',
    tr: 'transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/50 data-[expanded=true]:bg-gray-100/50 dark:data-[expanded=true]:bg-gray-800/50',
    td: 'whitespace-normal break-words text-sm md:text-base p-2 md:p-4',
    th: 'whitespace-normal break-words text-sm md:text-base p-2 md:p-4',
  },
}

// 跳转到扩展详情页
function navigateToExtension(extensionName: string): void {
  router.push(`/extension/${extensionName}`)
}

onMounted(async () => {
  try {
    await store.fetchLocalExtensions()
  }
  catch (err) {
    console.error('Failed to fetch extensions:', err)
  }
})
</script>

<template>
  <div :class="ui.container">
    <div v-if="store.loading" :class="ui.loadingWrapper">
      <USkeleton class="mx-auto h-6 w-full max-w-sm rounded-[calc(var(--ui-radius)*1.5)] md:h-8" />
      <USkeleton class="h-24 w-full rounded-[calc(var(--ui-radius)*1.5)] md:h-32" />
      <USkeleton class="h-24 w-full rounded-[calc(var(--ui-radius)*1.5)] md:h-32" />
    </div>
    <div v-else-if="store.error" :class="ui.errorAlert">
      <UAlert :title="store.error.message" color="error" variant="soft" icon="i-carbon-warning-alt" class="shadow-lg" />
    </div>
    <div v-else class="space-y-4 md:space-y-6">
      <UAlert :title="`当前共有 ${extensionsCount} 个 VSCode 扩展`" color="primary" variant="subtle" icon="i-carbon-data-vis-1" :class="ui.statsAlert" />

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

      <div :class="ui.tableWrapper">
        <div :class="ui.tableHeader">
          <div :class="ui.headerLeft">
            <UButton
              :disabled="table?.tableApi?.getFilteredSelectedRowModel().rows.length === 0"
              color="neutral"
              variant="outline"
              icon="i-carbon-copy"
              :class="ui.copyButton"
              @click="copySelectedCommands"
            >
              复制 ID
            </UButton>
          </div>

          <div :class="ui.headerCenter">
            <UPagination v-model:page="currentPage" :items-per-page="table?.tableApi?.getState().pagination.pageSize" :total="table?.tableApi?.getFilteredRowModel().rows.length" />
          </div>

          <div :class="ui.headerRight">
            <UDropdownMenu
              :items="
                table?.tableApi
                  ?.getAllColumns()
                  .filter((column) => column.getCanHide())
                  .map((column) => ({
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
              <UButton label="显示列" color="neutral" variant="outline" trailing-icon="i-carbon-chevron-down" :class="ui.columnButton" />
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
          :data="store.extensions"
          :columns="columns"
          :loading="store.loading"
          :pagination-options="{
            getPaginationRowModel: getPaginationRowModel(),
          }"
          :ui="ui.table"
          class="w-full"
        >
          <template #expanded="{ row }">
            <ExtensionExpandedContent :extension="row.original" />
          </template>

          <template #extension_name-cell="{ row }">
            <div class="group" :class="[ui.extensionId]">
              <span class="group-hover:underline" @click="navigateToExtension(row.original.extension_name)">{{ row.original.extension_name }}</span>
              <UButton icon="i-carbon-copy" color="primary" variant="ghost" size="xs" :class="ui.actionButton" @click.stop="copyExtensionIds([row.original.extension_name])" />
            </div>
          </template>

          <template #display_name-cell="{ row }">
            <UButton :href="row.original.marketplace_url" target="_blank" color="neutral" variant="link" :class="ui.extensionName">
              {{ row.original.display_name }}
            </UButton>
          </template>

          <template #categories-cell="{ row }">
            <div :class="ui.badgeWrapper">
              <UBadge v-for="category in row.original.categories" :key="category" :label="category" color="secondary" variant="subtle" size="sm" :class="ui.badge" />
            </div>
          </template>

          <template #tags-cell="{ row }">
            <div :class="ui.badgeWrapper">
              <UBadge v-for="tag in row.original.tags" :key="tag" :label="tag" color="secondary" variant="subtle" size="xs" :class="ui.badge" />
            </div>
          </template>

          <template #last_updated-cell="{ row }">
            <span :class="ui.dateText">
              {{ new Date(row.original.last_updated).toLocaleString() }}
            </span>
          </template>

          <template #actions-cell="{ row }">
            <ExtensionActions :extension="row.original" />
          </template>
        </UTable>

        <div :class="ui.tableFooter">
          <div>已选择 {{ table?.tableApi?.getFilteredSelectedRowModel().rows.length || 0 }} / {{ table?.tableApi?.getFilteredRowModel().rows.length || 0 }} 行</div>
          <div class="flex items-center gap-4">
            <USelect
              v-model="pagination.pageSize"
              :items="pageSizeOptions"
              placeholder="每页显示数量"
              :ui="{
                trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200',
              }"
              class="w-36"
            />
            <UPagination v-model:page="currentPage" :items-per-page="table?.tableApi?.getState().pagination.pageSize" :total="table?.tableApi?.getFilteredRowModel().rows.length" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
