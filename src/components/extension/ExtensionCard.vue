<script setup lang="ts">
  import type { Extension } from '@/types/extension'

  const props = defineProps<{
    extension: Extension
  }>()

  function formatDate(date: string) {
    return new Date(date).toLocaleDateString('zh-CN')
  }
</script>

<template>
  <UCard :ui="{ ring: 'ring-1 hover:ring-2', shadow: 'hover:shadow-lg' }" class="transition-all duration-200">
    <div class="flex items-start gap-4">
      <div class="flex-1">
        <router-link :to="`/extension/${extension.extensionName}`" class="group">
          <h3 class="group-hover:text-primary-500 text-lg font-semibold">
            {{ extension.displayName }}
          </h3>
        </router-link>
        <p class="mt-1 line-clamp-2 text-sm text-gray-500">
          {{ extension.shortDescription }}
        </p>
      </div>
    </div>
    <div class="mt-4">
      <div class="flex flex-wrap gap-2">
        <UBadge v-for="category in extension.categories" :key="category" size="sm">
          {{ category }}
        </UBadge>
      </div>
    </div>
    <div class="mt-4 flex items-center justify-between text-sm">
      <div class="flex items-center gap-2 text-gray-500">
        <UIcon name="i-heroicons-clock" />
        <span>{{ formatDate(extension.latest_version.lastUpdated) }}</span>
      </div>
      <UButton :to="extension.marketplaceUrl" target="_blank" color="primary" variant="soft" size="sm"> 查看详情 </UButton>
    </div>
  </UCard>
</template>
