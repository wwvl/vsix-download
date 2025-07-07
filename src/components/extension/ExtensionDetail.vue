<!-- eslint-disable vue/html-self-closing -->
<script setup lang="ts">
import type { Extension } from '@/types/extension'
import { computed, resolveComponent, toRefs } from 'vue'
import { useExtension } from '@/composables/useExtension'

const props = defineProps<{
  extension: Extension
}>()
// 解析组件
const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')
const UTooltip = resolveComponent('UTooltip')

const { extension } = toRefs(props) // 使用 toRefs 解构 props
const { copyInstallCommand } = useExtension()

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

// 计算属性生成基本信息
const extensionInfo = computed(() => [
  { icon: 'i-carbon-version', value: extension.value.latest_version || 'N/A', tooltip: '版本' },
  { icon: 'i-carbon-time', value: formatDate(extension.value.last_updated) || 'N/A', tooltip: '最后更新' },
  { icon: 'i-carbon-code', value: extension.value.extension_name || 'N/A', tooltip: '扩展 ID', copyable: true },
])

const ui = {
  headerTitle: 'text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white tracking-tight',
  headerButton: 'flex flex-wrap items-center gap-1.5 mt-4 lg:mt-0',
  sectionTitle: 'my-6 scroll-mt-[calc(48px+45px+var(--ui-header-height))] text-2xl font-bold text-[var(--ui-text-highlighted)] lg:scroll-mt-[calc(48px+var(--ui-header-height))]',
  infoList: 'list-disc pl-2',
  infoItem: 'flex items-center py-2',
  badgeContainer: 'mt-2 flex flex-wrap gap-2',
  tableContainer: 'flex w-full flex-1 flex-col overflow-x-auto rounded-[calc(var(--ui-radius)*1.5)] border border-(--ui-border) focus:outline-hidden',
}
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex-1">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <h1 :class="ui.headerTitle">
            {{ extension.display_name }}
          </h1>
          <div :class="ui.headerButton">
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
        <h2 :class="ui.sectionTitle">
          基本信息
        </h2>
        <ul :class="ui.infoList">
          <li v-for="(info, index) in extensionInfo" :key="index" :class="ui.infoItem">
            <UTooltip :text="info.tooltip">
              <UIcon :name="info.icon" class="mr-6" />
            </UTooltip>
            <div :class="info.copyable ? 'hover:text-primary-500 cursor-pointer transition-colors duration-300' : ''" @click="info.copyable && copyInstallCommand(info.value)">
              {{ info.value }}
            </div>
          </li>
        </ul>
      </div>

      <hr class="border-t border-[var(--ui-border)]">

      <div>
        <h2 :class="ui.sectionTitle">
          分类
        </h2>
        <div :class="ui.badgeContainer">
          <UBadge v-for="category in extension.categories" :key="category" color="secondary" variant="subtle">
            {{ category }}
          </UBadge>
        </div>
      </div>

      <hr class="border-t border-[var(--ui-border)]">
      <div>
        <h2 :class="ui.sectionTitle">
          标签
        </h2>
        <div :class="ui.badgeContainer">
          <UBadge v-for="tag in extension.tags" :key="tag" color="secondary" variant="subtle">
            {{ tag }}
          </UBadge>
        </div>
      </div>

      <hr class="border-t border-[var(--ui-border)]">
      <div>
        <h2 :class="ui.sectionTitle">
          版本历史
        </h2>
        <div :class="ui.tableContainer">
          <ExtensionVersionHistory :extension="extension" />
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
