<script setup>
import { computed } from 'vue'

const props = defineProps({
  entities: {
    type: Object,
    required: true,
  },
})

const entityLabels = {
  order_id: 'Order ID',
  email: 'Email',
  phone: 'Phone',
  amount: 'Amount',
  date: 'Date',
}

const entityRows = computed(() =>
  Object.entries(props.entities).map(([key, value]) => ({
    key,
    label: entityLabels[key] || key,
    value,
  })),
)
</script>

<template>
  <div class="detail-card">
    <div class="detail-card-heading">
      <h4>Extracted entities</h4>
      <span class="detail-count">{{ entityRows.length }} fields</span>
    </div>
    <div class="entity-list">
      <div v-for="entity in entityRows" :key="entity.key" class="entity-row">
        <span class="entity-label">{{ entity.label }}</span>
        <span :class="['entity-value', { 'entity-value--empty': !entity.value }]">
          {{ entity.value || 'Not found' }}
        </span>
      </div>
    </div>
  </div>
</template>
