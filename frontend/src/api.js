const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000'
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/$/, '')
const REQUEST_TIMEOUT_MS = 8000

function createRequestError(message, code) {
  const error = new Error(message)
  error.code = code
  return error
}

async function requestJson(path, options = {}) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      signal: controller.signal,
    })

    const payload = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(payload.detail || `Request failed with status ${response.status}`)
    }

    return payload
  } catch (error) {
    if (error.name === 'AbortError') {
      throw createRequestError(
        'The API request timed out. Make sure FastAPI is running and try again.',
        'TIMEOUT',
      )
    }

    if (error instanceof TypeError) {
      throw createRequestError(
        `Could not reach the FastAPI server at ${API_BASE_URL}. Start the backend and try again.`,
        'NETWORK_ERROR',
      )
    }

    throw error
  } finally {
    clearTimeout(timeoutId)
  }
}

export async function checkHealth() {
  return requestJson('/health')
}

export async function analyzeMessage(text) {
  return requestJson('/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  })
}
