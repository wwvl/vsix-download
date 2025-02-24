<script setup lang="ts">
import type { Extension } from '@/types/extension'
import { ref } from 'vue'

const props = defineProps<{
  extension: Extension
}>()

const toast = useToast()
const copied = ref(false)

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

function copy(value: string) {
  navigator.clipboard.writeText(value)
  copied.value = true

  toast.add({
    title: '已复制 VSCode 安装命令！',
    description: `命令：${value}`,
    icon: 'i-carbon-checkmark-outline',
    color: 'success',
  })

  setTimeout(() => {
    copied.value = false
  }, 2000)
}
</script>

<template>
  <UCard variant="outline">
    <div class="grid grid-cols-1 grid-rows-[auto_2.5rem_auto_auto] gap-2 h-full">
      <!-- 标题和描述 -->
      <div class="min-h-0">
        <a :href="`/extension/${props.extension.extension_name}`" class="group block" target="_blank" rel="noopener noreferrer">
          <h3 class="group-hover:text-primary-500 text-lg font-semibold truncate">
            {{ props.extension.display_name }}
          </h3>
        </a>
      </div>

      <div class="mt-1 text-sm text-gray-500 overflow-hidden h-10">
        <div class="line-clamp-2">
          {{ props.extension.short_description }}
        </div>
      </div>

      <!-- 分类标签 -->
      <div class="min-h-0 h-12 overflow-hidden mt-2">
        <div class="flex flex-wrap gap-2 line-clamp-2">
          <UBadge v-for="category in props.extension.categories" :key="category" color="primary" variant="soft" size="sm">
            {{ category }}
          </UBadge>
        </div>
      </div>

      <!-- 时间和版本信息 -->
      <div class="flex items-center justify-between text-sm min-h-0">
        <div class="flex items-center gap-2 text-gray-500">
          <UIcon name="i-carbon-time" />
          <span>{{ formatDate(props.extension.last_updated) }}</span>
        </div>
        <div class="flex items-center gap-2 text-gray-500">
          <UIcon name="i-carbon-version" />
          <span>{{ props.extension.latest_version }}</span>
        </div>
      </div>

      <!-- 安装命令和按钮 -->
      <div class="flex items-center gap-2 min-h-0">
        <div class="flex-grow rounded-[calc(var(--ui-radius)*1.5)] border border-(--ui-border) focus:outline-hidden overflow-x-auto flex items-center min-w-0" role="button" aria-label="复制到剪贴板">
          <div class="truncate flex-1 flex items-center gap-1">
            <UIcon name="i-carbon-chevron-right" class="text-gray-400 flex-shrink-0" />
            <div class="truncate">
              ext install {{ props.extension.extension_name }}
            </div>
          </div>
          <UTooltip :text="copied ? '已复制' : '复制到剪贴板'" :popper="{ arrow: true }">
            <UButton
              :color="copied ? 'success' : 'neutral'"
              variant="link"
              size="sm"
              :icon="copied ? 'i-carbon-checkmark' : 'i-carbon-copy'"
              aria-label="Copy to clipboard"
              class="bg-secondary-100 flex-shrink-0"
              @click.stop="copy(`ext install ${props.extension.extension_name}`)"
            />
          </UTooltip>
        </div>
        <UButton
          color="primary"
          variant="solid"
          size="sm"
          icon="i-carbon-add"
          aria-label="添加"
          class="bg-primary-500 flex-shrink-0"
        />
      </div>
    </div>
  </UCard>
</template>
