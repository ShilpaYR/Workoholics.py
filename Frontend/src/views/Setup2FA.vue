<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-form">
        <h2 class="auth-title">Setup Two-Factor Authentication</h2>
        <p class="setup-text">
          Setting up 2FA for <strong>{{ username }}</strong>. Please scan the QR code below using your Google Authenticator app.
        </p>
        <div class="qr-code-container">
          <img :src="qrCodeUrl" alt="TOTP QR Code">
        </div>
        <p class="secret-key-text">
          Or enter the secret key manually:
          <span class="secret-key">{{ secretKey }}</span>
        </p>
        <form @submit.prevent="confirmSetup">
          <div class="form-group">
            <label for="totp_code">Confirm Code (From App):</label>
            <input type="text" id="totp_code" v-model="totpCode" required>
          </div>
          <button type="submit" class="auth-button">Confirm Setup</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();

const username = ref('');
const secretKey = ref('');
const qrCodeUrl = ref('');
const totpCode = ref('');

onMounted(async () => {
  username.value = route.query.username;
  if (!username.value) {
    router.push('/employees');
    return;
  }
  try {
    const response = await axios.get(`http://127.0.0.1:5002/setup-2fa?username=${username.value}`);
    secretKey.value = response.data.secret_key;
    qrCodeUrl.value = response.data.qr_code;
  } catch (error) {
    console.error('Error fetching 2FA setup data:', error);
    router.push('/employees');
  }
});

async function confirmSetup() {
  try {
    await axios.post('http://127.0.0.1:5002/confirm-2fa', {
      username: username.value,
      totp_code: totpCode.value,
      secret: secretKey.value
    });
    router.push('/employees');
  } catch (error) {
    console.error('Error confirming 2FA setup:', error);
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

.setup-text {
  text-align: center;
  margin-bottom: 20px;
}

.qr-code-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.secret-key-text {
  text-align: center;
  margin-bottom: 20px;
}

.secret-key {
  display: block;
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
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
