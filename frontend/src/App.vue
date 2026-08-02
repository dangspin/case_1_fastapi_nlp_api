<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { analyzeMessage, checkHealth } from './api'
import MessageInput from './components/MessageInput.vue'
import ResultSummary from './components/ResultSummary.vue'

const SAMPLE_MESSAGE =
  'My order ORD-10482 has not arrived. Please contact me at customer@example.com.'

const message = ref(SAMPLE_MESSAGE)
const result = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const apiStatus = ref('checking')

const apiStatusText = computed(() => {
  const labels = {
    checking: 'Checking FastAPI...',
    connected: 'FastAPI connected locally',
    degraded: 'FastAPI model unavailable',
    offline: 'FastAPI offline',
  }

  return labels[apiStatus.value]
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

async function checkApiHealth() {
  apiStatus.value = 'checking'

  try {
    const health = await checkHealth()
    apiStatus.value = health.model_loaded ? 'connected' : 'degraded'
  } catch {
    apiStatus.value = 'offline'
  }
}

onMounted(() => {
  checkApiHealth()
})

watch(message, () => {
  if (errorMessage.value) {
    errorMessage.value = ''
  }
})
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
      <div class="api-status" :class="`api-status--${apiStatus}`">
        <span class="status-dot"></span>
        <span>{{ apiStatusText }}</span>
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
        <MessageInput
          v-model="message"
          :is-loading="isLoading"
          :error-message="errorMessage"
          @submit="submitAnalysis"
          @load-sample="loadSample"
        />

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

      <ResultSummary v-if="result" :result="result" />

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
