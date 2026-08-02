<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: String,
    required: true,
  },
  caption: {
    type: String,
    required: true,
  },
  variant: {
    type: String,
    default: 'default',
  },
})

const valueClasses = computed(() => {
  if (props.variant === 'category') {
    return 'category-value'
  }

  if (props.variant.startsWith('priority-')) {
    return ['priority-badge', `priority-badge--${props.variant.replace('priority-', '')}`]
  }

  if (props.variant === 'review-warning') {
    return ['review-value', 'review-value--warning']
  }

  return 'review-value'
})
</script>

<template>
  <div class="summary-card">
    <span class="card-label">{{ label }}</span>
    <strong :class="valueClasses">{{ value }}</strong>
    <span class="card-caption">{{ caption }}</span>
  </div>
</template>
