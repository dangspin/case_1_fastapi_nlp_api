import { computed, onMounted, ref } from 'vue'
import { checkHealth } from '../api'

const STATUS_LABELS = {
  checking: 'Checking FastAPI...',
  connected: 'FastAPI connected locally',
  degraded: 'FastAPI model unavailable',
  offline: 'FastAPI offline',
}

export function useApiHealth() {
  const apiStatus = ref('checking')

  const apiStatusText = computed(() => STATUS_LABELS[apiStatus.value])
  const canRetry = computed(() => apiStatus.value === 'offline' || apiStatus.value === 'degraded')

  async function checkApiHealth() {
    apiStatus.value = 'checking'

    try {
      const health = await checkHealth()
      apiStatus.value = health.model_loaded ? 'connected' : 'degraded'
    } catch {
      apiStatus.value = 'offline'
    }
  }

  function markOffline() {
    apiStatus.value = 'offline'
  }

  onMounted(checkApiHealth)

  return {
    apiStatus,
    apiStatusText,
    canRetry,
    checkApiHealth,
    markOffline,
  }
}
