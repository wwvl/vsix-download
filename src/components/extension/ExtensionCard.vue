<script setup lang="ts">
import type { Extension } from '@/types/extension'

const props = defineProps<{
  extension: Extension
}>()

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
</script>

<template>
  <UCard class="h-full">
    <div class="flex h-full flex-col">
      <div class="flex-grow">
        <a :href="`/extension/${props.extension.extension_name}`" class="group block" target="_blank" rel="noopener noreferrer">
          <h3 class="group-hover:text-primary-500 text-lg font-semibold">
            {{ props.extension.display_name }}
          </h3>
          <p class="mt-1 line-clamp-2 text-sm text-gray-500">
            {{ props.extension.short_description }}
          </p>
        </a>

        <div class="mt-4 flex flex-wrap gap-2">
          <UBadge v-for="category in props.extension.categories" :key="category" color="primary" variant="soft" size="sm">
            {{ category }}
          </UBadge>
        </div>
      </div>

      <div class="mt-4 flex flex-col gap-2">
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center gap-2 text-gray-500">
            <UIcon name="i-carbon-time" />
            <span>{{ formatDate(props.extension.last_updated) }}</span>
          </div>
          <div class="flex items-center gap-2 text-gray-500">
            <UIcon name="i-carbon-version" />
            <span>{{ props.extension.latest_version }}</span>
          </div>
        </div>
        <div class="flex items-center gap-2 text-sm text-gray-500">
          <UIcon name="i-carbon-terminal" />
          <code class="font-mono">ext install {{ props.extension.extension_name }}</code>
        </div>
      </div>
    </div>
  </UCard>
</template>
