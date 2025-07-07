<script setup lang="ts">
import { onMounted } from 'vue'
import { useExtensionStore } from '@/stores/extension'

const store = useExtensionStore()

onMounted(async () => {
  try {
    await store.fetchLocalExtensions()
  }
  catch (err) {
    console.error('Failed to fetch extensions:', err)
  }
})
</script>

<template>
  <div class="container mx-auto min-h-screen px-4 py-8 transition-all duration-300 sm:py-4 md:py-6">
    <div v-if="store.loading" class="space-y-4 text-center">
      <USkeleton class="mx-auto h-6 w-full max-w-sm rounded-[calc(var(--ui-radius)*1.5)] md:h-8" />
      <USkeleton class="h-24 w-full rounded-[calc(var(--ui-radius)*1.5)] md:h-32" />
      <USkeleton class="h-24 w-full rounded-[calc(var(--ui-radius)*1.5)] md:h-32" />
    </div>
    <div v-else-if="store.error" class="transform text-center transition-transform duration-300 hover:scale-[1.02]">
      <UAlert :title="store.error.message" color="error" variant="soft" icon="i-carbon-warning-alt" class="shadow-lg" />
    </div>
    <ExtensionList v-else :extensions="store.extensions" :loading="store.loading" :error="store.error" />
  </div>
</template>
