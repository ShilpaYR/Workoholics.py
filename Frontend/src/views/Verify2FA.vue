<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-form">
        <h2 class="auth-title">Verify Two-Factor Authentication</h2>
        <p class="verify-text">
          Please enter the 6-digit code from your Google Authenticator app for user <strong>{{ username }}</strong>.
        </p>
        <form @submit.prevent="verifyCode">
          <div class="form-group">
            <label for="totp_code">Authenticator Code:</label>
            <input type="text" id="totp_code" v-model="totpCode" required>
          </div>
          <button type="submit" class="auth-button">Verify Code</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { store } from '../store.js';

const route = useRoute();
const router = useRouter();

const username = ref('');
const totpCode = ref('');

onMounted(() => {
  username.value = route.query.username;
  if (!username.value) {
    router.push('/employees');
  }
});

async function verifyCode() {
  try {
    const response = await axios.post('http://127.0.0.1:5002/verify-2fa', {
      username: username.value,
      totp_code: totpCode.value
    });
    store.user = response.data.user;
    if (store.user.role === 'HRMgr') {
      router.push('/dashboard');
    } else {
      router.push('/employee-dashboard');
    }
  } catch (error) {
    console.error('Error verifying 2FA code:', error);
  }
}
</script>

<style scoped>
/* Add your component-specific styles here */
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.auth-card {
  width: 100%;
  max-width: 450px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.auth-title {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.verify-text {
  text-align: center;
  margin-bottom: 20px;
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
}
</style>
