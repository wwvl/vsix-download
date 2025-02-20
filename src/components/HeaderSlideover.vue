<script setup lang="ts">
  import type { HeaderMode, HeaderProps, HeaderSlots } from '@/types/header'
  import { createReusableTemplate } from '@vueuse/core'
  import { Primitive } from 'reka-ui'
  import { computed, ref, watch } from 'vue'
  import { useRoute } from 'vue-router'

  // Props 定义
  const props = withDefaults(defineProps<HeaderProps<HeaderMode>>(), {
    as: 'header',
    to: '/',
    title: 'Sub',
    toggleSide: 'right',
  })

  // 插槽定义
  const slots = defineSlots<HeaderSlots>()

  // 样式系统
  const ui = computed(() => ({
    root: 'bg-[var(--ui-bg)]/75 backdrop-blur border-b border-[var(--ui-border)] sticky top-0 z-50',
    container: 'flex items-center justify-between gap-3 h-[var(--ui-header-height)]',
    left: 'lg:flex-1 flex items-center gap-1.5',
    center: 'hidden lg:flex',
    right: 'flex items-center justify-end lg:flex-1 gap-1.5',
    title: 'shrink-0 font-bold text-xl text-[var(--ui-text-highlighted)] flex items-end gap-1.5',
    toggle: 'lg:hidden',
    content: 'lg:hidden',
    overlay: 'lg:hidden',
    header: '',
    body: 'p-4 sm:p-6 overflow-y-auto',
  }))

  // 状态管理
  const open = ref(false)
  const route = useRoute()
  const ariaLabel = ref('Sub')

  // 监听路由变化
  watch(
    () => route.fullPath,
    () => {
      open.value = false
    },
  )

  // 模板复用
  const [DefineLeftTemplate, ReuseLeftTemplate] = createReusableTemplate()
  const [DefineRightTemplate, ReuseRightTemplate] = createReusableTemplate()
  const [DefineToggleTemplate, ReuseToggleTemplate] = createReusableTemplate()
</script>

<template>
  <DefineToggleTemplate>
    <slot name="toggle" :open="open">
      <UButton
        v-if="!!slots.content"
        color="neutral"
        variant="ghost"
        :aria-label="`${open ? 'Close' : 'Open'} menu`"
        :icon="open ? 'i-carbon-close' : 'i-carbon-menu'"
        v-bind="typeof props.toggle === 'object' ? props.toggle : undefined"
        :class="[ui.toggle, props.toggle?.class]"
        @click="open = !open"
      />
    </slot>
  </DefineToggleTemplate>

  <DefineLeftTemplate>
    <div :class="ui.left">
      <ReuseToggleTemplate v-if="props.toggleSide === 'left'" />

      <slot name="left">
        <ULink :to="to" :aria-label="ariaLabel" :class="ui.title">
          <slot name="title">
            {{ title }}
          </slot>
        </ULink>
      </slot>
    </div>
  </DefineLeftTemplate>

  <DefineRightTemplate>
    <div :class="ui.right">
      <slot name="right" />

      <ReuseToggleTemplate v-if="props.toggleSide === 'right'" />
    </div>
  </DefineRightTemplate>

  <Primitive :as="as" :class="ui.root">
    <slot name="top" />

    <UContainer :class="ui.container">
      <ReuseLeftTemplate />

      <div :class="ui.center">
        <slot />
      </div>

      <ReuseRightTemplate />
    </UContainer>

    <slot name="bottom" />
  </Primitive>

  <USlideover
    v-if="!!slots.content"
    v-model:open="open"
    :ui="{
      overlay: ui.overlay,
      content: ui.content,
    }"
  >
    <template #content>
      <div :class="ui.header">
        <UContainer :class="ui.container">
          <ReuseLeftTemplate />

          <ReuseRightTemplate />
        </UContainer>
      </div>

      <div :class="ui.body">
        <slot name="content" />
      </div>
    </template>
  </USlideover>
</template>
