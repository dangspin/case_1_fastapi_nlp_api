<script setup>
import { computed, ref, watch } from 'vue'
import { analyzeMessage } from './api'
import { useApiHealth } from './composables/useApiHealth'
import MessageInput from './components/MessageInput.vue'
import ResultSummary from './components/ResultSummary.vue'

const SAMPLE_MESSAGE =
  'My order ORD-10482 has not arrived. Please contact me at customer@example.com.'

const message = ref(SAMPLE_MESSAGE)
const result = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const MAX_MESSAGE_LENGTH = 5000

const { apiStatus, apiStatusText, canRetry, checkApiHealth, markOffline } = useApiHealth()

const messageLength = computed(() => message.value.length)

const validationMessage = computed(() => {
  if (!message.value.trim()) {
    return 'Please enter a customer message first.'
  }

  if (messageLength.value > MAX_MESSAGE_LENGTH) {
    return `Message is too long. Please keep it to ${MAX_MESSAGE_LENGTH} characters or fewer.`
  }

  return ''
})

function loadSample() {
  message.value = SAMPLE_MESSAGE
  errorMessage.value = ''
}

async function submitAnalysis() {
  if (validationMessage.value) {
    result.value = null
    return
  }

  const cleanedMessage = message.value.trim()

  isLoading.value = true
  errorMessage.value = ''

  try {
    result.value = await analyzeMessage(cleanedMessage)
  } catch (error) {
    if (error.code === 'NETWORK_ERROR' || error.code === 'TIMEOUT') {
      markOffline()
    }

    errorMessage.value = error.message || 'The API request could not be completed.'
    result.value = null
  } finally {
    isLoading.value = false
  }
}

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
        <span aria-live="polite">{{ apiStatusText }}</span>
        <button
          v-if="canRetry"
          class="status-retry"
          type="button"
          @click="checkApiHealth"
        >
          Retry
        </button>
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
          :validation-message="validationMessage"
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
