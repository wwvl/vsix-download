<script setup lang="ts">
import { useExtensionStore } from '@/stores/extension'
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const store = useExtensionStore()

const extensionId = computed(() => route.params.id as string)
const extension = computed(() => store.extensions.find(ext => ext.extension_name === extensionId.value))

onMounted(async () => {
  if (!store.extensions.length) {
    await store.fetchExtensions()
  }
})
</script>

<template>
  <UContainer class="py-8">
    <template v-if="store.loading">
      <USkeleton class="h-64" />
    </template>
    <template v-else-if="extension">
      <ExtensionDetail :extension="extension" />
    </template>
    <template v-else>
      <UAlert title="未找到扩展" description="该扩展不存在或已被删除" color="error" />
    </template>
  </UContainer>
</template>
