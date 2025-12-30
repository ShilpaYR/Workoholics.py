<template>
  <header class="app-header">
    <div class="container">
      <div class="logo">
        <router-link to="/">HR Management</router-link>
      </div>
      <nav>
        <ul>
          <template v-if="!store.user">
            <li><router-link to="/">Home</router-link></li>
            <li><router-link to="/employees">Employees</router-link></li>
            <li><router-link to="/career-page">Career Page</router-link></li>
            <li><router-link to="/contact-us">Contact Us</router-link></li>
          </template>
          <template v-else>
            <template v-if="store.user.role === 'HRMgr'">
              <li><router-link to="/dashboard">Dashboard</router-link></li>
              <li><router-link to="/job-list">Applications</router-link></li>
            </template>
            <template v-else-if="store.user.role === 'Applicant'">
              <li><router-link to="/job-list">Job Listings</router-link></li>
            </template>
            <template v-else>
              <li><router-link to="/dashboard">Dashboard</router-link></li>
              <li><router-link to="/queries">Queries</router-link></li>
            </template>
            <li><a href="#" @click.prevent="logout">Sign Out</a></li>
          </template>
        </ul>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { store } from '../store.js';
import { useRouter } from 'vue-router';

const router = useRouter();

function logout() {
  store.user = null;
  router.push('/');
}
</script>

<style scoped>
.app-header {
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-family: 'Poppins', sans-serif;
  width: 100%;
}

.container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.logo a {
  font-size: 1.8rem;
  font-weight: 600;
  color: #007bff;
  text-decoration: none;
}

nav ul {
  list-style: none;
  display: flex;
  gap: 1.5rem;
  margin: 0;
  padding: 0;
}

nav a {
  color: #333;
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: 500;
  transition: color 0.3s ease;
}

nav a:hover, nav a.router-link-exact-active {
  color: #007bff;
}
</style>
