<script setup>
import { computed } from 'vue'

const props = defineProps({
  percent: {
    type: Number,
    required: true,
  },
})

const safePercent = computed(() => Math.min(100, Math.max(0, props.percent)))
</script>

<template>
  <div class="confidence-meter">
    <div class="meter-heading">
      <span>Model confidence</span>
      <strong>{{ safePercent }}%</strong>
    </div>
    <div class="meter-track">
      <div class="meter-fill" :style="{ width: `${safePercent}%` }"></div>
    </div>
  </div>
</template>
