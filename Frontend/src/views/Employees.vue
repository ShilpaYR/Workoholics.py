<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-form">
        <h2 class="auth-title">Employee Sign In</h2>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="login-username">Username</label>
            <input type="text" id="login-username" v-model="loginForm.username" required>
          </div>
          <div class="form-group">
            <label for="login-password">Password</label>
            <input type="password" id="login-password" v-model="loginForm.password" required>
          </div>
          <button type="submit" class="auth-button">Sign In</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const router = useRouter();
const errorMessage = ref('');

const loginForm = ref({
  username: '',
  password: ''
});

async function login() {
  errorMessage.value = '';
  try {
    const response = await axios.post('http://127.0.0.1:5002/employee-signin', loginForm.value);
    if (response.data.redirect) {
      router.push({ path: response.data.redirect, query: { username: loginForm.value.username } });
    } else {
      // Fallback for other cases
      store.user = response.data.user;
      if (store.user.role === 'HRMgr') {
        router.push('/dashboard');
      } else {
        router.push('/employee-dashboard');
      }
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'An unexpected error occurred.';
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  background-color: #f0f2f5;
  padding: 2rem 0;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.auth-form {
  padding: 30px;
}

.auth-title {
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.auth-button {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.auth-button:hover {
  background-color: #0056b3;
}

.error-message {
  color: #d9534f;
  text-align: center;
  margin-bottom: 15px;
}
</style>
