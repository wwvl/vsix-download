<script setup lang="ts">
import type { Extension } from '@/types/extension'
import { defineProps, toRefs } from 'vue'

const props = defineProps<{
  extension: Extension
}>()

// 使用 toRefs 解构 props
const { extension } = toRefs(props)

function getDownloadUrl(extensionName: string, version: string): string {
  const [publisher, name] = extensionName.split('.')
  return `https://marketplace.visualstudio.com/_apis/public/gallery/publishers/${publisher}/vsextensions/${name}/${version}/vspackage`
}
</script>

<template>
  <div class="max-w-2xl space-y-2">
    <div
      v-for="(version, index) in extension.version_history"
      :key="index"
      class="flex items-center justify-between p-2 text-sm transition-all hover:bg-gray-100 dark:hover:bg-gray-700/50"
    >
      <span>v{{ version.version }}</span>
      <span>{{ new Date(version.lastUpdated).toLocaleString() }}</span>
      <UTooltip :text="`下载 v${version.version}`">
        <UButton
          size="xs"
          color="primary"
          icon="i-carbon-download"
          :label="`${extension.extension_name}-${version.version}.vsix`"
          :href="getDownloadUrl(extension.extension_name, version.version)"
          target="_blank"
          class="hover:scale-110 transition-transform"
        />
      </UTooltip>
    </div>
  </div>
</template>
