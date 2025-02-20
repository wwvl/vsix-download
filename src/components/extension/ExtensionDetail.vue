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
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold">
            {{ extension.displayName }}
          </h1>
          <p class="mt-2 text-gray-500">
            {{ extension.extensionName }}
          </p>
        </div>
        <UButton :to="extension.marketplaceUrl" target="_blank" color="primary" icon="i-heroicons-arrow-top-right-on-square"> 在 Marketplace 中查看 </UButton>
      </div>
    </template>

    <div class="space-y-6">
      <div>
        <h2 class="text-lg font-semibold">描述</h2>
        <p class="mt-2">
          {{ extension.shortDescription }}
        </p>
      </div>

      <div>
        <h2 class="text-lg font-semibold">分类</h2>
        <div class="mt-2 flex flex-wrap gap-2">
          <UBadge v-for="category in extension.categories" :key="category" color="primary">
            {{ category }}
          </UBadge>
        </div>
      </div>

      <div>
        <h2 class="text-lg font-semibold">标签</h2>
        <div class="mt-2 flex flex-wrap gap-2">
          <UBadge v-for="tag in extension.tags" :key="tag" color="gray" variant="soft">
            {{ tag }}
          </UBadge>
        </div>
      </div>

      <div>
        <h2 class="text-lg font-semibold">版本历史</h2>
        <UTable
          :columns="[
            { key: 'version', label: '版本' },
            { key: 'lastUpdated', label: '更新时间' },
          ]"
          :rows="extension.version_history"
        >
          <template #lastUpdated-data="{ row }">
            {{ formatDate(row.lastUpdated) }}
          </template>
        </UTable>
      </div>
    </div>

    <template #footer>
      <UButton :href="extension.downloadUrl" target="_blank" color="primary" icon="i-heroicons-arrow-down-tray"> 下载 VSIX </UButton>
    </template>
  </UCard>
</template>
