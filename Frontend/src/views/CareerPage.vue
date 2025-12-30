<template>
  <div class="auth-container">
    <!-- Logged-in user view -->
    <div v-if="user" class="logged-in-card">
      <h2 class="welcome-message">Welcome, {{ user.name }}!</h2>
      <p>You are now signed in.</p>
      <button @click="proceedToJobs" class="auth-button">Proceed to Job Listings</button>
      <button @click="logout" class="logout-button">Logout</button>
    </div>

    <!-- Guest view (Sign in/Sign up) -->
    <div v-else class="auth-card">
      <div class="auth-form">
        <p v-if="loginMessage" class="success-message">{{ loginMessage }}</p>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <button @click="signInWithGoogle" class="google-signin-button">
          <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google logo" />
          <span>Sign in with Google</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { store } from '../store.js';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const errorMessage = ref('');
const loginMessage = ref('');
const user = ref(store.user);

const isCareerPage = computed(() => route.path === '/career-page');

// Check for user session when the component mounts
onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:5002/get-user', { withCredentials: true });
    if (response.data && response.data.email) {
      store.user = response.data;
      user.value = store.user;
    }
  } catch (error) {
    console.log('No user session found on mount.');
  }
});

function proceedToJobs() {
  if (store.user.role === 'HRMgr') {
    router.push('/dashboard');
  } else {
    router.push('/job-list');
  }
}

function signInWithGoogle() {
  window.location.href = 'http://localhost:5002/google-login';
}

async function logout() {
  try {
    await axios.post('http://localhost:5002/logout', {}, { withCredentials: true });
    store.user = null;
    user.value = null;
    loginMessage.value = 'You have been successfully logged out.';
  } catch (error) {
    errorMessage.value = 'Failed to log out. Please try again.';
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

.career-title {
  text-align: center;
  font-size: 1.5rem; /* Adjusted for space */
  font-weight: bold;
  margin-bottom: 1rem;
  color: #333;
}

.auth-card, .logged-in-card {
  width: 100%;
  max-width: 400px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.logged-in-card {
  padding: 40px;
  text-align: center;
}

.welcome-message {
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.auth-form {
  padding: 30px;
}

.auth-title {
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
}

.auth-button, .logout-button {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 4px;
  background-color: #007bff;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 10px;
}

.auth-button:hover {
  background-color: #0056b3;
}

.logout-button {
  background-color: #dc3545;
  margin-top: 15px;
}

.logout-button:hover {
  background-color: #c82333;
}

.google-signin-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #fff;
  color: #333;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 10px;
}

.google-signin-button:hover {
  background-color: #f0f0f0;
}

.google-signin-button img {
  width: 20px;
  height: 20px;
}

.error-message {
  color: #d9534f;
  text-align: center;
  margin-bottom: 15px;
}

.success-message {
  color: #5cb85c;
  text-align: center;
  margin-bottom: 15px;
}
</style>
