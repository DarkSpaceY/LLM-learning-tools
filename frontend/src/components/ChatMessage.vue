<template>
  <div :class="['chat-message', role]">
    <div class="message-content">
      <div v-html="content"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  role: {
    type: String,
    required: true
  },
  content: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.chat-message {
  margin-bottom: 1.5rem;
  max-width: 85%;
  opacity: 0;
  transform: translateY(20px);
  animation: messageAppear 0.3s ease forwards;
}

.chat-message.user {
  margin-left: auto;
}

.message-content {
  padding: 0.5rem 0.75rem;
  border-radius: 12px;
  background-color: #f7f7f8;
  color: #353740;
  line-height: 1.2;
  font-size: 0.9375rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  white-space: pre-wrap;
  word-wrap: break-word;
  display: inline-block;
  max-width: 100%;
  word-break: break-word;
}

.chat-message.user .message-content {
  background-color: #10a37f;
  color: #ffffff;
}

@keyframes messageAppear {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 