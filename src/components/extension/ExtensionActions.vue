<script setup lang="ts">
import type { DropdownMenuItem } from '@nuxt/ui'
import type { Extension } from '@/types/extension'
import { computed } from 'vue'
import { useExtension } from '@/composables/useExtension'

const props = defineProps<{
  extension: Extension
}>()

const { getDownloadUrl, copyInstallCommand } = useExtension()

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
