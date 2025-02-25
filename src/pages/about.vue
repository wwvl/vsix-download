<script setup lang="ts">
const downloadLinks = [
  {
    title: 'GitHub 直链',
    url: 'https://github.com/wwvl/vsix-download/blob/main/extension_downloader.py',
    isChina: false,
  },
  {
    title: 'ghproxy.net 加速',
    url: 'https://ghproxy.net/https://raw.githubusercontent.com/wwvl/vsix-download/main/extension_downloader.py',
    isChina: true,
  },
  {
    title: 'jsDelivr CDN',
    url: 'https://fastly.jsdelivr.net/gh/wwvl/vsix-download@main/extension_downloader.py',
    isChina: true,
  },
  {
    title: 'wget.la 加速',
    url: 'https://wget.la/https://raw.githubusercontent.com/wwvl/vsix-download/main/extension_downloader.py',
    isChina: true,
  },
]
</script>

<template>
  <div class="container mx-auto min-h-screen max-w-3xl px-4 py-8">
    <!-- 头部区域 -->
    <div class="mb-12 text-center">
      <h1 class="text-primary mb-4 text-4xl font-bold">
        VSCode 扩展下载工具
      </h1>
      <p class="mb-6 text-lg text-gray-600 dark:text-gray-400">
        一个简单的 VSCode 扩展下载脚本
      </p>
      <div class="flex justify-center gap-4">
        <UButton label="查看文档" icon="i-carbon-document" to="https://github.com/wwvl/vsix-download#readme" target="_blank" />
        <UButton label="GitHub" color="neutral" variant="outline" icon="i-simple-icons:github" to="https://github.com/wwvl/vsix-download" target="_blank" />
      </div>
    </div>

    <!-- 脚本下载 -->
    <div class="mb-12">
      <h2 class="mb-6 text-2xl font-semibold">
        脚本下载
      </h2>
      <div class="grid gap-4">
        <UCard v-for="link in downloadLinks" :key="link.title" class="transition-transform hover:scale-[1.01]">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <h3 class="font-medium">
                {{ link.title }}
              </h3>
              <UBadge v-if="link.isChina" color="primary" variant="soft" size="sm">
                国内加速
              </UBadge>
            </div>
            <UButton :to="link.url" target="_blank" icon="i-carbon-download" label="下载" size="sm" />
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>
