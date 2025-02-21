<script setup lang="ts">
  import { onMounted, onUnmounted, ref } from 'vue'

  // 添加滚动状态
  const isAtBottom = ref(false)

  // 滚动到指定位置
  function scrollToPosition(position: 'top' | 'bottom') {
    window.scrollTo({
      top: position === 'top' ? 0 : document.body.scrollHeight,
      behavior: 'smooth',
    })
  }

  // 监听滚动位置
  onMounted(() => {
    const handleScroll = () => {
      const scrolledToBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100
      isAtBottom.value = scrolledToBottom
    }
    window.addEventListener('scroll', handleScroll)
    handleScroll() // 初始检查

    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
    })
  })
</script>

<template>
  <div class="fixed right-6 bottom-6 z-50">
    <UButton
      :icon="isAtBottom ? 'i-carbon-arrow-up' : 'i-carbon-arrow-down'"
      color="primary"
      variant="solid"
      size="lg"
      class="transform rounded-full shadow-lg transition-all duration-300 hover:scale-110"
      :title="isAtBottom ? '回到顶部' : '前往底部'"
      @click="scrollToPosition(isAtBottom ? 'top' : 'bottom')"
    />
  </div>
</template>
