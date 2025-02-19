<script setup lang="ts">
  import { useDark, useToggle } from '@vueuse/core'

  const isDark = useDark()
  const toggleDark = useToggle(isDark)
</script>

<template>
  <UTooltip :text="`Switch to ${isDark ? 'light' : 'dark'} mode`">
    <UButton :icon="isDark ? 'i-carbon-moon' : 'i-carbon-sun'" color="neutral" variant="ghost" :aria-label="`Switch to ${isDark ? 'light' : 'dark'} mode`" @click="toggleDark()" />
  </UTooltip>
</template>
