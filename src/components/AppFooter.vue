<script setup lang="ts"></script>

<template>
  <USeparator />
  <Footer>
    <template #left>
      <p class="text-sm text-(--ui-text-muted)">
        Copyright © {{ new Date().getFullYear() }} <a href="https://www.zxj.asia" target="_blank">wwvl</a>. Theme by
        <UButton color="primary" variant="subtle" href="https://ui3.nuxt.dev/" target="_blank" label="NuxtUI" size="xs" />
      </p>
    </template>

    <!-- <UNavigationMenu :items="items" variant="link" /> -->

    <template #right>
      <ColorModeSelect />

      <UTooltip text="GitHub">
        <UButton icon="i-carbon-logo-github" color="neutral" variant="ghost" href="https://github.com/wwvl/vsix-download" rel="noopener noreferrer" aria-label="GitHub" />
      </UTooltip>
    </template>
  </Footer>
</template>
