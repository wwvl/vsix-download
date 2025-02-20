<script setup lang="ts">
  import { useExtensionStore } from '@/stores/extension'
  import { computed, onMounted } from 'vue'
  import { useRoute } from 'vue-router'

  const route = useRoute()
  const store = useExtensionStore()

  const extensionId = computed(() => route.params.id as string)
  const extension = computed(() => store.extensions.find((ext) => ext.extensionName === extensionId.value))
  const loading = computed(() => store.loading)

  onMounted(() => {
    if (!store.extensions.length) {
      store.fetchExtensions()
    }
  })
</script>

<template>
  <UContainer class="py-8">
    <template v-if="loading">
      <USkeleton class="h-64" />
    </template>
    <template v-else-if="extension">
      <ExtensionDetail :extension="extension" />
    </template>
    <template v-else>
      <UAlert title="未找到扩展" description="该扩展不存在或已被删除" color="red" />
    </template>
  </UContainer>
</template>
