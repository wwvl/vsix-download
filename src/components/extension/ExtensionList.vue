<script setup lang="ts">
import type { Extension } from '@/types/extension'

defineProps<{
  extensions: Extension[]
}>()
</script>

<template>
  <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
    <ExtensionCard v-for="extension in extensions" :key="extension.extension_name" :extension="extension" />
  </div>
</template>
