<!-- eslint-disable vue/html-self-closing -->
<script setup lang="ts">
import type { Extension } from '@/types/extension'
import { useClipboard } from '@vueuse/core'
import { computed, h, resolveComponent, toRefs } from 'vue'

const props = defineProps<{
  extension: Extension
}>()
// 解析组件
const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UTable = resolveComponent('UTable')
const UTooltip = resolveComponent('UTooltip')

// 定义 info 的类型
interface Info {
  row: {
    original: {
      version: string
      lastUpdated: string
    }
  }
}

const { extension } = toRefs(props) // 使用 toRefs 解构 props

const { copy } = useClipboard()

const toast = useToast()
// 复制安装命令到剪贴板
function copyExtensionName(extensionName: string): Promise<void> {
  return copy(`ext install ${extensionName}`).then(() => {
    toast.add({
      title: '安装命令已复制！',
      description: `命令：ext install ${extensionName}`,
      icon: 'i-carbon-checkmark-outline',
      color: 'success',
    })
  })
}

function formatDate(date: string) {
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

// 获取下载链接
function getDownloadUrl(extensionName: string, version: string): string {
  if (!extensionName)
    return '#' // 如果没有 extensionName，返回一个默认链接
  const [publisher, name] = extensionName.split('.')
  return `https://marketplace.visualstudio.com/_apis/public/gallery/publishers/${publisher}/vsextensions/${name}/${version}/vspackage`
}

// 计算属性生成基本信息
const extensionInfo = computed(() => [
  { icon: 'i-carbon-version', value: extension.value.latest_version || 'N/A', tooltip: '版本' },
  { icon: 'i-carbon-time', value: formatDate(extension.value.last_updated) || 'N/A', tooltip: '最后更新' },
  { icon: 'i-carbon-code', value: extension.value.extension_name || 'N/A', tooltip: '扩展 ID', copyable: true },
])

// 定义列
const columns = [
  { accessorKey: 'version', header: 'Version' },
  { accessorKey: 'lastUpdated', header: 'Updated At', cell: (info: Info) => formatDate(info.row.original.lastUpdated) },
  {
    accessorKey: 'download',
    header: 'Download',
    cell: (info: Info) => {
      const version = info.row.original.version // 获取当前行的版本
      const extension_name = extension.value.extension_name // 获取 extension_name
      const downloadText = `${extension_name}-${version}.vsix` // 格式化文本
      return h(
        UButton,
        {
          href: getDownloadUrl(extension_name, version),
          target: '_blank',
          color: 'primary',
        },
        () => downloadText,
      )
    },
  },
]
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex-1">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <h1
            class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white tracking-tight"
          >
            {{ extension.display_name }}
          </h1>
          <div class="flex flex-wrap items-center gap-1.5 mt-4 lg:mt-0">
            <UButton :href="extension.marketplace_url" target="_blank" color="neutral" variant="outline" icon="i-logos-microsoft-icon">
              Marketplace
            </UButton>
          </div>
        </div>
        <div class="mt-4 text-lg text-gray-500 dark:text-gray-400">
          {{ extension.short_description }}
        </div>
      </div>
    </template>

    <div class="space-y-6">
      <div>
        <h2 class="my-6 scroll-mt-[calc(48px+45px+var(--ui-header-height))] text-2xl font-bold text-[var(--ui-text-highlighted)] lg:scroll-mt-[calc(48px+var(--ui-header-height))]">
          基本信息
        </h2>
        <ul class="extension-info list-disc pl-2">
          <li v-for="(info, index) in extensionInfo" :key="index" class="flex items-center py-2">
            <UTooltip :text="info.tooltip">
              <UIcon :name="info.icon" class="mr-2" />
            </UTooltip>
            <div :class="info.copyable ? 'hover:text-primary-500 cursor-pointer transition-colors duration-300' : ''" @click="info.copyable && copyExtensionName(info.value) ">
              {{ info.value }}
            </div>
          </li>
        </ul>
      </div>

      <hr class="border-t border-[var(--ui-border)]">

      <div>
        <h2 class="my-6 scroll-mt-[calc(48px+45px+var(--ui-header-height))] text-2xl font-bold text-[var(--ui-text-highlighted)] lg:scroll-mt-[calc(48px+var(--ui-header-height))]">
          分类
        </h2>
        <div class="mt-2 flex flex-wrap gap-2">
          <UBadge v-for="category in extension.categories" :key="category" color="secondary" variant="subtle">
            {{ category }}
          </UBadge>
        </div>
      </div>

      <hr class="border-t border-[var(--ui-border)]">
      <div>
        <h2 class="my-6 scroll-mt-[calc(48px+45px+var(--ui-header-height))] text-2xl font-bold text-[var(--ui-text-highlighted)] lg:scroll-mt-[calc(48px+var(--ui-header-height))]">
          标签
        </h2>
        <div class="mt-2 flex flex-wrap gap-2">
          <UBadge v-for="tag in extension.tags" :key="tag" color="secondary" variant="subtle">
            {{ tag }}
          </UBadge>
        </div>
      </div>

      <hr class="border-t border-[var(--ui-border)]">
      <div>
        <h2 class="my-6 scroll-mt-[calc(48px+45px+var(--ui-header-height))] text-2xl font-bold text-[var(--ui-text-highlighted)] lg:scroll-mt-[calc(48px+var(--ui-header-height))]">
          版本历史
        </h2>
        <div class="flex w-full flex-1 flex-col overflow-x-auto rounded-[calc(var(--ui-radius)*1.5)] border border-(--ui-border) focus:outline-hidden">
          <UTable
            :data="extension.version_history"
            :columns="columns"
            class="mt-2"
            :ui="{
              tr: 'transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/50 data-[expanded=true]:bg-gray-100/50 dark:data-[expanded=true]:bg-gray-800/50',
            }"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <UButton :href="extension.download_url" target="_blank" color="primary" icon="i-heroicons-arrow-down-tray">
        下载 VSIX
      </UButton>
    </template>
  </UCard>
</template>
