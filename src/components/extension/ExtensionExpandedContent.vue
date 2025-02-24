<script setup lang="ts">
import type { Extension } from '@/types/extension'

defineProps<{
  extension: Extension
}>()

// UI 配置
const ui = {
  expandedContent: 'bg-gray-50/50 p-4 md:p-6 transition-all duration-300 dark:bg-gray-800/30',
  descriptionWrapper: 'mb-4 md:mb-6 transform transition-all duration-300 hover:scale-[1.01]',
  descriptionTitle: 'mb-2 md:mb-3 text-base md:text-lg font-medium text-gray-900 dark:text-gray-100',
  descriptionText: 'text-sm md:text-base leading-relaxed text-gray-600 dark:text-gray-300',
}
</script>

<template>
  <div :class="ui.expandedContent">
    <div :class="ui.descriptionWrapper">
      <h3 :class="ui.descriptionTitle">
        扩展描述
      </h3>
      <p :class="ui.descriptionText">
        {{ extension.short_description }}
      </p>
    </div>
    <h3 :class="ui.descriptionTitle">
      版本历史
    </h3>
    <ExtensionVersionHistory :extension="extension" :visible-version-count="6" />
  </div>
</template>
