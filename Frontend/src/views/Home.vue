<template>
  <div class="home-container">
    <h1>Welcome to our CMPE272 Project</h1>
    <p class="subtitle">Under guidance of Prof. Andrew Bond</p>
  </div>
</template>

<script setup>
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 120px);
  text-align: center;
}
h1 {
    font-size: 5rem;
    font-weight: bold;
}
.subtitle {
    font-size: 2rem;
    margin-top: 1rem;
}
</style>
