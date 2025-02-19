<script setup lang="ts">
  import { computed } from 'vue'

  const items = computed(() => [
    {
      label: 'wwvl',
      href: 'https://www.wwvl.asia',
      target: '_blank',
      rel: 'noopener noreferrer',
    },
    {
      label: 'Github',
      href: 'https://github.com/wwvl',
      target: '_blank',
      rel: 'noopener noreferrer',
    },
  ])
</script>

<template>
  <HeaderSlideover :toggle="{ color: 'primary', variant: 'subtle', class: 'rounded-full' }" toggle-side="right">
    <template #title>
      <Logo class="h-6 w-auto" />
      <ULink as="button"> vsix-download </ULink>
    </template>

    <UNavigationMenu :items="items" />

    <template #right>
      <ColorModeButton />

      <UTooltip text="Open on GitHub">
        <UButton color="neutral" variant="ghost" as="a" href="https://github.com/wwvl" target="_blank" rel="noopener noreferrer" icon="i-carbon-logo-github" aria-label="GitHub" />
      </UTooltip>
    </template>

    <template #content>
      <UNavigationMenu :items="items" orientation="vertical" class="-mx-2.5" />
    </template>
  </HeaderSlideover>
</template>
