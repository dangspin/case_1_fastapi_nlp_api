<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
  errorMessage: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'submit', 'load-sample'])

function updateMessage(event) {
  emit('update:modelValue', event.target.value)
}
</script>

<template>
  <article class="panel input-panel">
    <div class="panel-heading">
      <div>
        <p class="eyebrow">01 / INPUT</p>
        <h3>Customer message</h3>
      </div>
      <button class="text-button" type="button" @click="emit('load-sample')">Load sample</button>
    </div>

    <label class="sr-only" for="customer-message">Customer message</label>
    <textarea
      id="customer-message"
      :value="modelValue"
      class="message-input"
      :disabled="isLoading"
      placeholder="Paste a customer-support message here..."
      @input="updateMessage"
      @keydown.ctrl.enter="emit('submit')"
      @keydown.meta.enter="emit('submit')"
    ></textarea>

    <div class="input-footer">
      <span class="helper-text">Tip: press Ctrl/Cmd + Enter to analyze</span>
      <button class="primary-button" type="button" :disabled="isLoading" @click="emit('submit')">
        <span v-if="isLoading" class="button-spinner"></span>
        {{ isLoading ? 'Analyzing...' : 'Analyze message' }}
      </button>
    </div>

    <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>
  </article>
</template>
