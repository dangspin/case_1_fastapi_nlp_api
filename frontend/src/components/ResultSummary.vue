<script setup>
import { computed } from 'vue'
import EntityList from './EntityList.vue'

const props = defineProps({
  result: {
    type: Object,
    required: true,
  },
})

const confidencePercent = computed(() => Math.round(props.result.confidence * 100))
</script>

<template>
  <section class="results-section" aria-live="polite">
    <div class="section-heading">
      <div>
        <p class="eyebrow">03 / RESULT</p>
        <h3>Structured ticket</h3>
      </div>
      <span class="confidence-label">{{ confidencePercent }}% confidence</span>
    </div>

    <div class="summary-grid">
      <div class="summary-card">
        <span class="card-label">Category</span>
        <strong class="category-value">{{ result.category }}</strong>
        <span class="card-caption">ML classification</span>
      </div>
      <div class="summary-card">
        <span class="card-label">Priority</span>
        <strong class="priority-badge" :class="`priority-badge--${result.priority}`">
          {{ result.priority }}
        </strong>
        <span class="card-caption">Rule-based routing</span>
      </div>
      <div class="summary-card">
        <span class="card-label">Review status</span>
        <strong :class="['review-value', { 'review-value--warning': result.needs_review }]">
          {{ result.needs_review ? 'Needs review' : 'Ready to route' }}
        </strong>
        <span class="card-caption">Confidence threshold: 70%</span>
      </div>
    </div>

    <div class="details-grid">
      <EntityList :entities="result.entities" />

      <div class="detail-card">
        <div class="detail-card-heading">
          <h4>Useful keywords</h4>
          <span class="detail-count">{{ result.keywords.length }} found</span>
        </div>
        <div class="keyword-list">
          <span v-for="keyword in result.keywords" :key="keyword" class="keyword-chip">
            {{ keyword }}
          </span>
          <span v-if="result.keywords.length === 0" class="empty-state">No keywords found.</span>
        </div>

        <div class="confidence-meter">
          <div class="meter-heading">
            <span>Model confidence</span>
            <strong>{{ confidencePercent }}%</strong>
          </div>
          <div class="meter-track">
            <div class="meter-fill" :style="{ width: `${confidencePercent}%` }"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
