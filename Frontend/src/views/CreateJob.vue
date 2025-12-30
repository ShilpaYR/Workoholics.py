<template>
  <div class="create-job-container">
    <div class="form-card">
      <div class="card-header">
        <h1 class="form-title">Create a New Job</h1>
        <p class="form-subtitle">Fill out the details below to post a new job opening.</p>
      </div>
      <form @submit.prevent="submitJob" class="job-form">
        <div class="form-group">
          <label for="job-title">Job Title</label>
          <input type="text" id="job-title" v-model="jobTitle" placeholder="e.g., Senior Frontend Developer" required>
        </div>
        <div class="form-group">
          <label for="job-description">Job Description</label>
          <textarea id="job-description" v-model="jobDescription" rows="6" placeholder="Describe the role, responsibilities, and qualifications..." required></textarea>
        </div>
        <div class="form-actions">
          <router-link to="/job-list" class="btn-cancel">Cancel</router-link>
          <button type="submit" class="btn-submit">Post Job</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const jobTitle = ref('');
const jobDescription = ref('');
const router = useRouter();

const submitJob = async () => {
  if (!jobTitle.value || !jobDescription.value) {
    alert('Please fill in all fields.');
    return;
  }

  try {
    await axios.post('http://127.0.0.1:5002/jobs', {
      job_title: jobTitle.value,
      job_description: jobDescription.value
    });
    router.push('/job-list'); // Redirect to job list after successful creation
  } catch (error) {
    console.error('Error creating job:', error);
    alert('Failed to create job. Please try again.');
  }
};
</script>

<style scoped>
.create-job-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
  font-family: 'Poppins', sans-serif;
  padding: 40px;
}

.form-card {
  width: 100%;
  max-width: 600px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #6e8efb, #a777e3);
  color: white;
  padding: 40px;
  text-align: center;
}

.form-title {
  font-size: 2.5em;
  font-weight: 700;
  margin: 0;
}

.form-subtitle {
  font-size: 1.1em;
  margin: 10px 0 0;
  opacity: 0.9;
}

.job-form {
  padding: 40px;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
  font-size: 1.1em;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 1em;
  font-family: 'Poppins', sans-serif;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #6e8efb;
  box-shadow: 0 0 0 3px rgba(110, 142, 251, 0.2);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 30px;
}

.btn-cancel,
.btn-submit {
  padding: 12px 25px;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1em;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.btn-cancel {
  background: #f0f2f5;
  color: #555;
}

.btn-cancel:hover {
  background: #e0e2e5;
}

.btn-submit {
  background: linear-gradient(135deg, #6e8efb, #a777e3);
  color: white;
  box-shadow: 0 8px 20px rgba(110, 142, 251, 0.3);
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(110, 142, 251, 0.5);
}
</style>