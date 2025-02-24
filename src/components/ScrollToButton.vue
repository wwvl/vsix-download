<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'

interface Props {
  // 滚动速度，单位毫秒
  duration?: number
  // 自定义滚动目标元素 ID
  targetId?: string
  // 是否显示进度条
  showProgress?: boolean
  // 进度条颜色
  progressColor?: string
}

const props = withDefaults(defineProps<Props>(), {
  duration: 500,
  targetId: '',
  showProgress: true,
  progressColor: 'var(--ui-primary)',
})

// 添加滚动状态
const isAtBottom = ref(false)
const scrollProgress = ref(0)
const showButton = ref(false)

// 计算滚动进度
function calculateScrollProgress() {
  const winScroll = document.documentElement.scrollTop
  const height = document.documentElement.scrollHeight - document.documentElement.clientHeight
  scrollProgress.value = (winScroll / height) * 100
}

// 检查是否显示按钮
function checkShowButton() {
  const scrollTop = document.documentElement.scrollTop || document.body.scrollTop
  const windowHeight = window.innerHeight
  showButton.value = scrollTop > windowHeight * 0.3 // 滚动超过 30% 时显示
}

// 滚动到指定位置
function scrollToPosition(position: 'top' | 'bottom' | 'custom') {
  let targetPosition = 0

  if (position === 'bottom') {
    targetPosition = document.body.scrollHeight
  }
  else if (position === 'custom' && props.targetId) {
    const element = document.getElementById(props.targetId)
    if (element) {
      targetPosition = element.offsetTop
    }
  }

  window.scrollTo({
    top: targetPosition,
    behavior: props.duration <= 0 ? 'auto' : 'smooth',
  })
}

// 监听滚动位置
onMounted(() => {
  const handleScroll = () => {
    const scrolledToBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100
    isAtBottom.value = scrolledToBottom

    if (props.showProgress) {
      calculateScrollProgress()
    }

    checkShowButton()
  }

  window.addEventListener('scroll', handleScroll)
  handleScroll() // 初始检查

  onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
  })
})

// 计算进度条样式
const progressStyle = computed(() => ({
  width: `${scrollProgress.value}%`,
  backgroundColor: props.progressColor,
  position: 'fixed' as const,
  top: 0,
  left: 0,
  height: '3px',
  transition: 'width 0.3s',
  zIndex: 100,
}))
</script>

<template>
  <div>
    <!-- 进度条 -->
    <div v-if="showProgress" :style="progressStyle" />

    <!-- 滚动按钮 -->
    <div v-show="showButton" class="fixed right-6 bottom-6 z-50 flex flex-col gap-2">
      <UButton
        v-if="targetId"
        icon="i-carbon-arrow-right"
        color="primary"
        variant="solid"
        size="lg"
        class="transform rounded-full shadow-lg transition-all duration-300 hover:scale-110"
        title="滚动到指定位置"
        @click="scrollToPosition('custom')"
      />

      <UTooltip :text="isAtBottom ? '回到顶部' : '前往底部'">
        <UButton
          :icon="isAtBottom ? 'i-lucide-arrow-up-to-line' : 'i-lucide-arrow-down-to-line'"
          color="primary"
          variant="solid"
          size="lg"
          class="transform rounded-full shadow-lg transition-all duration-300 hover:scale-110"
          :title="isAtBottom ? '回到顶部' : '前往底部'"
          @click="scrollToPosition(isAtBottom ? 'top' : 'bottom')"
        />
      </UTooltip>
    </div>
  </div>
</template>
