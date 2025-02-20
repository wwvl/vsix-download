<script setup lang="ts">
  import type { Extension } from '@/types/extension'

  const props = defineProps<{
    extension: Extension
  }>()

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('zh-CN')
  }
</script>

<template>
  <UCard class="h-full">
    <div class="flex h-full flex-col">
      <div class="flex-grow">
        <router-link :to="`/extension/${extension.extensionName}`" class="group block">
          <h3 class="group-hover:text-primary-500 text-lg font-semibold">
            {{ extension.displayName }}
          </h3>
          <p class="mt-1 line-clamp-2 text-sm text-gray-500">
            {{ extension.shortDescription }}
          </p>
        </router-link>

        <div class="mt-4 flex flex-wrap gap-2">
          <UBadge v-for="category in extension.categories" :key="category" color="primary" variant="soft" size="sm">
            {{ category }}
          </UBadge>
        </div>
      </div>

      <div class="mt-4 flex items-center justify-between text-sm">
        <div class="flex items-center gap-2 text-gray-500">
          <UIcon name="i-carbon-time" />
          <span>{{ formatDate(extension.latest_version.lastUpdated) }}</span>
        </div>
        <UButton :to="extension.marketplaceUrl" target="_blank" color="primary" variant="soft" size="sm"> 查看详情 </UButton>
      </div>
    </div>
  </UCard>
</template>
