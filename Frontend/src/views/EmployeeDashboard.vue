<template>
  <div class="employee-dashboard">
    <div class="dashboard-header">
      <h1>Welcome to your Dashboard</h1>
      <p>Here you can find all the information you need.</p>
    </div>
    <div class="dashboard-content">
      <div class="dashboard-card">
        <h3>My Profile</h3>
        <p>View and update your personal information.</p>
        <button class="dashboard-button">View Profile</button>
      </div>
      <div class="dashboard-card">
        <h3>My Tasks</h3>
        <p>Check your assigned tasks and their deadlines.</p>
        <button class="dashboard-button">View Tasks</button>
      </div>
      <div class="dashboard-card">
        <h3>Company News</h3>
        <p>Stay up-to-date with the latest company news.</p>
        <button class="dashboard-button">View News</button>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.employee-dashboard {
  padding: 2rem;
  font-family: 'Poppins', sans-serif;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2.5rem;
  font-weight: bold;
  color: #333;
}

.dashboard-header p {
  font-size: 1.2rem;
  color: #777;
}

.dashboard-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.dashboard-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.dashboard-card:hover {
  transform: translateY(-5px);
}

.dashboard-card h3 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 1rem;
}

.dashboard-card p {
  color: #555;
  margin-bottom: 1.5rem;
}

.dashboard-button {
  background-color: #007bff;
  color: #fff;
  padding: 0.8rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.dashboard-button:hover {
  background-color: #0056b3;
}
</style>
