<template>
  <div class="chat-container">
    <div class="chat-messages">
      <div v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
        <div class="message-content">{{ message.content }}</div>
      </div>
    </div>
    <div class="chat-input">
      <input type="text" v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type your message..." />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const newMessage = ref('');
const messages = ref([]);

const sendMessage = async () => {
  if (newMessage.value.trim() === '') return;

  const userMessage = newMessage.value;
  messages.value.push({ role: 'user', content: userMessage });
  newMessage.value = '';

  try {
    const response = await axios.post('http://127.0.0.1:5002/chatbot', {
      query: userMessage,
    });
    messages.value.push({ role: 'computer', content: response.data.response });
  } catch (error) {
    console.error('Error sending message:', error);
    messages.value.push({ role: 'computer', content: 'Sorry, I am having trouble connecting. Please try again later.' });
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
  max-width: 800px;
  margin: 30px auto;
  border: 1px solid #ccc;
  border-radius: 8px;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  max-width: 70%;
}

.message.user {
  align-self: flex-end;
}

.message.computer {
  align-self: flex-start;
}

.message-content {
  padding: 0.8rem 1.2rem;
  border-radius: 1.2rem;
  font-size: 1rem;
}

.message.user .message-content {
  background-color: #007bff;
  color: #fff;
  border-top-right-radius: 0;
}

.message.computer .message-content {
  background-color: #f0f2f5;
  color: #333;
  border-top-left-radius: 0;
}

.chat-input {
  display: flex;
  padding: 1rem;
  border-top: 1px solid #ccc;
}

.chat-input input {
  flex: 1;
  padding: 0.8rem;
  border: 1px solid #ccc;
  border-radius: 2rem;
  font-size: 1rem;
}

.chat-input button {
  margin-left: 1rem;
  padding: 0.8rem 1.2rem;
  border: none;
  border-radius: 2rem;
  background-color: #007bff;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
}
</style>
