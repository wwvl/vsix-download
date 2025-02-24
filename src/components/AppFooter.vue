<script setup lang="ts">
// const items = [
//   {
//     label: 'Releases',
//     to: 'https://github.com/wwvl',
//     target: '_blank',
//   },
// ]
</script>

<template>
  <USeparator />
  <Footer>
    <template #left>
      <p class="text-sm text-(--ui-text-muted)">
        Copyright © 2024-{{ new Date().getFullYear() }}
        <a href="https://github.com/wwvl" target="_blank">wwvl</a>
      </p>
    </template>

    <!-- <UNavigationMenu :items="items" variant="link" /> -->

    <template #right>
      <ColorModeSelect />

      <UTooltip text="GitHub">
        <UButton icon="i-carbon-logo-github" color="neutral" variant="ghost" href="https://github.com/wwvl" rel="noopener noreferrer" aria-label="GitHub" />
      </UTooltip>
    </template>
  </Footer>
</template>
