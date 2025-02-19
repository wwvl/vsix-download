<script setup lang="ts">
// const router = useRouter()
</script>

<template>
  <div class="flex h-screen flex-col items-center justify-center gap-4">
    <h1 class="text-2xl font-bold text-(--ui-primary)">
      Nuxt UI v3 - Vue Playground
    </h1>

    <div class="flex items-center gap-2">
      <UButton label="Documentation" icon="i-carbon-play-outline" as="a" href="https://ui3.nuxt.dev/getting-started/installation/vue" target="_blank" rel="noopener noreferrer" />

      <UButton label="GitHub" color="neutral" variant="outline" icon="i-simple-icons:github" as="a" href="https://github.com/nuxt/ui" target="_blank" rel="noopener noreferrer" />
    </div>
  </div>
</template>
