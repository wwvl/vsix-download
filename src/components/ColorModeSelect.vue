<script setup lang="ts">
  import { useColorMode } from '@vueuse/core'
  import { computed } from 'vue'

  const mode = useColorMode()
  const items = computed(() => [
    // { label: 'System', value: 'auto', icon: 'i-carbon-screen' },
    { label: 'Light', value: 'light', icon: 'i-carbon-sun' },
    { label: 'Dark', value: 'dark', icon: 'i-carbon-moon' },
  ])

  const preference = computed({
    get() {
      return items.value.find((option) => option.value === mode.value) || items.value[0]
    },
    set(option) {
      mode.value = option?.value as 'light' | 'dark'
    },
  })
</script>

<template>
  <USelectMenu v-model="preference" :search-input="false" :icon="preference?.icon" :items="items" highlight />
</template>
