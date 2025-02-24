<script setup lang="ts">
import { useExtensionStore } from '@/stores/extension'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const store = useExtensionStore()

// 分页配置
const PAGE_SIZE = 36
const currentPage = ref(1)

// 分页数据计算
const paginatedExtensions = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  const end = start + PAGE_SIZE
  return store.extensions.slice(start, end)
})

// 总页数计算
const totalPages = computed(() => Math.ceil(store.extensions.length / PAGE_SIZE))

// 监听路由参数变化
watch(
  () => route.query.page,
  (newPage) => {
    const page = Number(newPage) || 1
    // 页码验证
    if (page < 1 || (totalPages.value > 0 && page > totalPages.value)) {
      router.replace({ query: { page: '1' } })
      return
    }
    currentPage.value = page
  },
  { immediate: true },
)

onMounted(() => {
  store.fetchExtensions()
})

// 分页链接处理
function paginationTo(page: number) {
  return { query: { page } }
}

// 错误信息处理
const errorMessage = computed(() => {
  if (!store.error)
    return ''
  return store.error instanceof Error ? store.error.message : String(store.error)
})
</script>

<template>
  <div class="min-h-screen p-4">
    <UContainer>
      <UCard class="mb-6">
        <template #header>
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold">
                VS Code 扩展市场
              </h1>
              <p class="mt-2 text-gray-500">
                浏览和搜索 Visual Studio Code 扩展
              </p>
            </div>
          </div>
        </template>
      </UCard>

      <UAlert v-if="store.error" color="warning" variant="soft" icon="i-carbon-warning" title="加载失败" :description="errorMessage" class="mb-6" />

      <div v-if="store.loading" class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div v-for="i in 6" :key="i" class="flex flex-col gap-4 rounded-xl border p-4">
          <div class="flex items-center gap-3">
            <USkeleton class="h-10 w-10 rounded-lg" />
            <div class="flex-1">
              <USkeleton class="mb-2 h-4 w-3/4" />
              <USkeleton class="h-3 w-1/2" />
            </div>
          </div>
          <USkeleton class="h-20" />
          <div class="flex flex-wrap gap-2">
            <USkeleton v-for="j in 3" :key="j" class="h-6 w-16" />
          </div>
        </div>
      </div>

      <template v-else-if="!store.error">
        <ExtensionList :extensions="paginatedExtensions" class="mt-6" />

        <div v-if="totalPages > 1" class="mt-6 flex justify-center">
          <UPagination
            v-model="currentPage"
            :total="store.extensions.length"
            :page-size="PAGE_SIZE"
            :sibling-count="2"
            show-edges
            color="primary"
            variant="soft"
            active-color="primary"
            active-variant="solid"
            size="md"
            :to="paginationTo"
            :ui="{
              root: 'flex items-center gap-2',
              list: 'flex items-center gap-1',
            }"
          />
        </div>
      </template>
    </UContainer>
  </div>
</template>
