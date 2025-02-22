<script setup lang="ts">
  import type { Extension } from '@/types/extension'
  import type { DropdownMenuItem, TableColumn } from '@nuxt/ui'
  import type { Column } from '@tanstack/vue-table'
  import { useExtensionStore } from '@/stores/extension'
  import { getPaginationRowModel } from '@tanstack/vue-table'
  import { useClipboard } from '@vueuse/core'
  import { upperFirst } from 'scule'
  import { computed, h, onMounted, ref, resolveComponent, watch } from 'vue'

  const store = useExtensionStore()
  const toast = useToast()
  const { copy } = useClipboard()
  const UButton = resolveComponent('UButton')
  const UCheckbox = resolveComponent('UCheckbox')
  const UDropdownMenu = resolveComponent('UDropdownMenu')
  const UPagination = resolveComponent('UPagination')
  const UInput = resolveComponent('UInput')

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

  // 添加全局搜索状态
  const globalFilter = ref('')

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

  // 获取表头组件
  function getHeader(column: Column<Extension>, label: string) {
    const isSorted = column.getIsSorted()

    return h(UButton, {
      color: 'neutral',
      variant: 'ghost',
      label,
      icon:
        isSorted ?
          isSorted === 'asc' ?
            'i-carbon-arrow-up'
          : 'i-carbon-arrow-down'
        : 'i-carbon-arrows-vertical',
      class: '-mx-2.5',
      onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
    })
  }

  // 获取下载链接
  function getDownloadUrl(extensionName: string, version: string): string {
    const [publisher, name] = extensionName.split('.')
    return `https://marketplace.visualstudio.com/_apis/public/gallery/publishers/${publisher}/vsextensions/${name}/${version}/vspackage`
  }

  // 复制安装命令到剪贴板
  function copyInstallCommand(extensionId: string): Promise<void> {
    return copy(`ext install ${extensionId}`).then(() => {
      toast.add({
        title: '安装命令已复制！',
        description: `命令：ext install ${extensionId}`,
        icon: 'i-carbon-checkmark-outline',
        color: 'success',
      })
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

    const ids = selectedRows.map((row: any) => row.original.extension_name).join('\n')
    await copy(ids)
    toast.add({
      title: '已复制选中的扩展 ID！',
      description: `共复制 ${selectedRows.length} 个扩展 ID`,
      icon: 'i-carbon-checkmark-outline',
      color: 'success',
    })
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
          modelValue: table.getIsSomePageRowsSelected() ? 'indeterminate' : table.getIsAllPageRowsSelected(),
          'onUpdate:modelValue': (value: boolean | 'indeterminate') => table.toggleAllPageRowsSelected(!!value),
          ariaLabel: '选择全部',
        }),
      cell: ({ row }) =>
        h(UCheckbox, {
          modelValue: row.getIsSelected(),
          'onUpdate:modelValue': (value: boolean | 'indeterminate') => row.toggleSelected(!!value),
          ariaLabel: '选择行',
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
    return Object.fromEntries(columns.filter((col) => (col as any).accessorKey).map((col) => [(col as any).accessorKey, labels[(col as any).accessorKey] || upperFirst((col as any).accessorKey)]))
  })

  function getDropdownActions(extension: Extension): DropdownMenuItem[][] {
    return [
      [
        {
          label: '复制安装命令',
          icon: 'i-lucide-copy',
          onSelect: () => {
            copyInstallCommand(extension.extension_name)
          },
        },
      ],
      [
        {
          label: '下载',
          icon: 'i-carbon-download',
          href: getDownloadUrl(extension.extension_name, extension.latest_version),
          target: '_blank',
        },
        {
          label: '查看详情',
          icon: 'i-lucide-external-link',
          href: extension.marketplace_url,
          target: '_blank',
        },
      ],
    ]
  }

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
    expandedContent: 'bg-gray-50/50 p-4 md:p-6 transition-all duration-300 dark:bg-gray-800/30',
    descriptionWrapper: 'mb-4 md:mb-6 transform transition-all duration-300 hover:scale-[1.01]',
    descriptionTitle: 'mb-2 md:mb-3 text-base md:text-lg font-medium text-gray-900 dark:text-gray-100',
    descriptionText: 'text-sm md:text-base leading-relaxed text-gray-600 dark:text-gray-300',
    versionHistoryWrapper: 'transform transition-all duration-300 hover:scale-[1.01]',
    versionHistoryTitle: 'mb-2 md:mb-3 text-base md:text-lg font-medium text-gray-900 dark:text-gray-100',
    versionList: 'space-y-2 md:space-y-3',
    versionItem: 'flex items-center gap-2 md:gap-3 rounded-[calc(var(--ui-radius)*1.5)] p-2 transition-colors duration-300 hover:bg-gray-100 dark:hover:bg-gray-700/50 text-sm md:text-base',
    versionBadge: 'min-w-[50px] md:min-w-[60px] justify-center text-xs md:text-sm',
    versionDate: 'flex-1 text-xs md:text-sm text-gray-600 dark:text-gray-300',
    downloadButton: 'transform transition-all duration-300 hover:scale-110',
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

  onMounted(async () => {
    try {
      await store.fetchExtensions()
    } catch (err) {
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

            <UInput v-model="globalFilter" placeholder="搜索扩展..." icon="i-carbon-search" :class="ui.searchInput" />
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
            <div :class="ui.expandedContent">
              <div :class="ui.descriptionWrapper">
                <h3 :class="ui.descriptionTitle">扩展描述</h3>
                <p :class="ui.descriptionText">
                  {{ row.original.short_description }}
                </p>
              </div>

              <div :class="ui.versionHistoryWrapper">
                <h3 :class="ui.versionHistoryTitle">版本历史</h3>
                <div :class="ui.versionList">
                  <div v-for="(version, index) in row.original.version_history" :key="index" :class="ui.versionItem">
                    <UBadge color="primary" variant="subtle" :class="ui.versionBadge">
                      {{ version.version }}
                    </UBadge>
                    <span :class="ui.versionDate">
                      {{ new Date(version.lastUpdated).toLocaleString() }}
                    </span>
                    <UTooltip :text="`下载 v${version.version}`">
                      <UButton
                        size="xs"
                        color="primary"
                        variant="ghost"
                        icon="i-carbon-download"
                        :href="getDownloadUrl(row.original.extension_name, version.version)"
                        target="_blank"
                        :class="ui.downloadButton"
                      />
                    </UTooltip>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <template #extension_name-cell="{ row }">
            <div :class="ui.extensionId" @click="() => copyInstallCommand(row.original.extension_name)">
              {{ row.original.extension_name }}
            </div>
          </template>

          <template #display_name-cell="{ row }">
            <UButton :href="row.original.marketplace_url" target="_blank" color="neutral" variant="link" :class="ui.extensionName">
              {{ row.original.display_name }}
            </UButton>
          </template>

          <template #categories-cell="{ row }">
            <div :class="ui.badgeWrapper">
              <UBadge v-for="category in row.original.categories" :key="category" :label="category" color="primary" variant="subtle" size="sm" :class="ui.badge" />
            </div>
          </template>

          <template #tags-cell="{ row }">
            <div :class="ui.badgeWrapper">
              <UBadge v-for="tag in row.original.tags" :key="tag" :label="tag" color="neutral" variant="subtle" size="xs" :class="ui.badge" />
            </div>
          </template>

          <template #last_updated-cell="{ row }">
            <span :class="ui.dateText">
              {{ new Date(row.original.last_updated).toLocaleString() }}
            </span>
          </template>

          <template #actions-cell="{ row }">
            <div class="flex justify-end">
              <UDropdownMenu :items="getDropdownActions(row.original)">
                <UButton icon="i-carbon-overflow-menu-vertical" color="neutral" variant="ghost" :class="ui.actionButton" />
              </UDropdownMenu>
            </div>
          </template>
        </UTable>

        <div :class="ui.tableFooter">
          <div>已选择 {{ table?.tableApi?.getFilteredSelectedRowModel().rows.length || 0 }} / {{ table?.tableApi?.getFilteredRowModel().rows.length || 0 }} 行</div>
          <UPagination v-model:page="currentPage" :items-per-page="table?.tableApi?.getState().pagination.pageSize" :total="table?.tableApi?.getFilteredRowModel().rows.length" />
        </div>
      </div>
    </div>
  </div>
</template>
