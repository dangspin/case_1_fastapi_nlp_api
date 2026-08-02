<script setup>
import { computed } from 'vue'
import EntityList from './EntityList.vue'
import SummaryCard from './SummaryCard.vue'
import ConfidenceMeter from './ConfidenceMeter.vue'

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
      <SummaryCard
        label="Category"
        :value="result.category"
        caption="ML classification"
        variant="category"
      />
      <SummaryCard
        label="Priority"
        :value="result.priority"
        caption="Rule-based routing"
        :variant="`priority-${result.priority}`"
      />
      <SummaryCard
        label="Review status"
        :value="result.needs_review ? 'Needs review' : 'Ready to route'"
        caption="Confidence threshold: 70%"
        :variant="result.needs_review ? 'review-warning' : 'review'"
      />
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

        <ConfidenceMeter :percent="confidencePercent" />
      </div>
    </div>
  </section>
</template>
