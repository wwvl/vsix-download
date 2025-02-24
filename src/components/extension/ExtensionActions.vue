<script setup lang="ts">
import type { Extension } from '@/types/extension'
import type { DropdownMenuItem } from '@nuxt/ui'
import { useClipboard } from '@vueuse/core'
import { computed } from 'vue'

const props = defineProps<{
  extension: Extension
}>()

const toast = useToast()
const { copy } = useClipboard()

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

const dropdownActions = computed<DropdownMenuItem[][]>(() => [
  [
    {
      label: '复制安装命令',
      icon: 'i-lucide-copy',
      onSelect: () => {
        copyInstallCommand(props.extension.extension_name)
      },
    },
  ],
  [
    {
      label: '下载',
      icon: 'i-carbon-download',
      href: getDownloadUrl(props.extension.extension_name, props.extension.latest_version),
      target: '_blank',
    },
    {
      label: '查看详情',
      icon: 'i-lucide-external-link',
      href: props.extension.marketplace_url,
      target: '_blank',
    },
  ],
])
</script>

<template>
  <div class="flex justify-end">
    <UDropdownMenu :items="dropdownActions">
      <UButton icon="i-carbon-overflow-menu-vertical" color="neutral" variant="ghost" class="transform transition-all duration-300 hover:scale-110" />
    </UDropdownMenu>
  </div>
</template>
