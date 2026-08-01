<script setup>
import { computed, ref } from 'vue'
import { analyzeMessage } from './api'

const SAMPLE_MESSAGE =
  'My order ORD-10482 has not arrived. Please contact me at customer@example.com.'

const message = ref(SAMPLE_MESSAGE)
const result = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

const entityLabels = {
  order_id: 'Order ID',
  email: 'Email',
  phone: 'Phone',
  amount: 'Amount',
  date: 'Date',
}

const entityRows = computed(() => {
  if (!result.value) {
    return []
  }

  return Object.entries(result.value.entities).map(([key, value]) => ({
    key,
    label: entityLabels[key] || key,
    value,
  }))
})

const confidencePercent = computed(() => {
  if (!result.value) {
    return 0
  }

  return Math.round(result.value.confidence * 100)
})

function loadSample() {
  message.value = SAMPLE_MESSAGE
  errorMessage.value = ''
}

async function submitAnalysis() {
  const cleanedMessage = message.value.trim()

  if (!cleanedMessage) {
    errorMessage.value = 'Please enter a customer message first.'
    result.value = null
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    result.value = await analyzeMessage(cleanedMessage)
  } catch (error) {
    errorMessage.value = error.message || 'The API request could not be completed.'
    result.value = null
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand-lockup">
        <span class="brand-mark">NLP</span>
        <div>
          <p class="eyebrow">CUSTOMER SUPPORT AUTOMATION</p>
          <h1>Ticket Intelligence</h1>
        </div>
      </div>
      <div class="api-status">
        <span class="status-dot"></span>
        <span>FastAPI connected locally</span>
      </div>
    </header>

    <main class="page-content">
      <section class="hero-copy">
        <p class="eyebrow">HYBRID NLP WORKFLOW</p>
        <h2>Turn customer messages into structured tickets.</h2>
        <p class="hero-description">
          Classify the issue, extract important fields, and identify priority in one API request.
        </p>
      </section>

      <section class="workspace-grid">
        <article class="panel input-panel">
          <div class="panel-heading">
            <div>
              <p class="eyebrow">01 / INPUT</p>
              <h3>Customer message</h3>
            </div>
            <button class="text-button" type="button" @click="loadSample">Load sample</button>
          </div>

          <label class="sr-only" for="customer-message">Customer message</label>
          <textarea
            id="customer-message"
            v-model="message"
            class="message-input"
            :disabled="isLoading"
            placeholder="Paste a customer-support message here..."
            @keydown.ctrl.enter="submitAnalysis"
            @keydown.meta.enter="submitAnalysis"
          ></textarea>

          <div class="input-footer">
            <span class="helper-text">Tip: press Ctrl/Cmd + Enter to analyze</span>
            <button class="primary-button" type="button" :disabled="isLoading" @click="submitAnalysis">
              <span v-if="isLoading" class="button-spinner"></span>
              {{ isLoading ? 'Analyzing...' : 'Analyze message' }}
            </button>
          </div>

          <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>
        </article>

        <article class="panel flow-panel">
          <p class="eyebrow">02 / PIPELINE</p>
          <h3>What happens next?</h3>

          <div class="flow-list">
            <div class="flow-step flow-step--active">
              <span class="step-number">01</span>
              <div>
                <strong>Classify</strong>
                <span>billing · delivery · technical</span>
              </div>
            </div>
            <div class="flow-connector"></div>
            <div class="flow-step">
              <span class="step-number">02</span>
              <div>
                <strong>Extract</strong>
                <span>order ID · email · amount · date</span>
              </div>
            </div>
            <div class="flow-connector"></div>
            <div class="flow-step">
              <span class="step-number">03</span>
              <div>
                <strong>Prioritize</strong>
                <span>low · medium · high</span>
              </div>
            </div>
          </div>

          <div class="tech-stack">
            <span>FastAPI</span>
            <span>Vue 3</span>
            <span>scikit-learn</span>
          </div>
        </article>
      </section>

      <section v-if="result" class="results-section" aria-live="polite">
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

      <section v-else class="empty-result" aria-live="polite">
        <span class="empty-result-icon">→</span>
        <div>
          <h3>Your structured ticket will appear here.</h3>
          <p>Enter a message and run the analysis to see the Vue interface consume the FastAPI response.</p>
        </div>
      </section>
    </main>

    <footer class="page-footer">
      <span>Vue 3 learning project</span>
      <span>FastAPI · TF-IDF · Regex extraction</span>
    </footer>
  </div>
</template>
