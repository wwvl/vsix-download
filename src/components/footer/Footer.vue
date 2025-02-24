<script setup lang="ts">
import type { FooterSlots } from '@/types/footer'
import { Primitive } from 'reka-ui'

const slots = defineSlots<FooterSlots>()

const ui = {
  root: '',
  top: 'py-8 lg:py-12',
  bottom: 'py-8 lg:py-12',
  container: 'py-8 lg:py-4 lg:flex lg:items-center lg:justify-between lg:gap-x-3',
  left: 'flex items-center justify-center lg:justify-start lg:flex-1 gap-x-1.5 mt-3 lg:mt-0 lg:order-1',
  center: 'mt-3 lg:mt-0 lg:order-2 flex items-center justify-center',
  right: 'lg:flex-1 flex items-center justify-center lg:justify-end gap-x-1.5 lg:order-3',
}
</script>

<template>
  <Primitive as="footer" :class="ui.root">
    <div v-if="!!slots.top" :class="ui.top">
      <slot name="top" />
    </div>

    <UContainer :class="ui.container">
      <div :class="ui.right">
        <slot name="right" />
      </div>

      <div :class="ui.center">
        <slot />
      </div>

      <div :class="ui.left">
        <slot name="left" />
      </div>
    </UContainer>

    <div v-if="!!slots.bottom" :class="ui.bottom">
      <slot name="bottom" />
    </div>
  </Primitive>
</template>
