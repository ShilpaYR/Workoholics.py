<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="main-title">Current Job Openings</h1>
      <div class="button-container">
        <router-link v-if="store.user && store.user.role === 'HRMgr'" to="/create" class="btn-create">Create New Job</router-link>
      </div>
    </div>
    <div class="job-listing-page">
      <div class="job-list-container">
        <div v-if="jobs.length === 0" class="no-jobs">
          <p>No job postings yet. Be the first to create one!</p>
        </div>
        <div v-else class="job-grid">
          <div v-for="job in jobs" :key="job.job_id" class="job-card" @click="selectJob(job)">
            <h2>{{ job.job_title }}</h2>
            <p class="job-id">Job ID: {{ job.job_id }}</p>
            <p>Date Posted: {{ job.date_posted }}</p>
          </div>
        </div>
      </div>
      <div class="job-details-container">
        <div v-if="selectedJob" class="job-details-card">
          <div class="card-header">
            <h1 class="job-title">{{ selectedJob.job_title }}</h1>
            <p class="job-id">Job ID: {{ selectedJob.job_id }}</p>
          </div>
          <div class="card-body">
            <p class="job-description">{{ selectedJob.job_description }}</p>
            <div v-if="store.user.role === 'Applicant'" class="application-form-card">
              <div class="card-header">
                <h2 class="form-title">Apply for this Position</h2>
              </div>
              <div class="card-body">
                <form @submit.prevent="submitApplication">
                  <div class="form-group">
                    <label for="applicant-name">Full Name</label>
                    <input type="text" id="applicant-name" v-model="applicantName" placeholder="e.g., Jane Doe" required>
                  </div>
                  <div class="form-group">
                    <label for="applicant-email">Email Address</label>
                    <input type="email" id="applicant-email" v-model="applicantEmail" placeholder="e.g., jane.doe@example.com" required>
                  </div>
                  <div class="form-group">
                    <label for="resume">Upload Resume</label>
                    <input type="file" id="resume" @change="handleFileChange" required>
                  </div>
                  <div v-if="submissionStatus" class="submission-status">
                    <p>{{ submissionStatus }}</p>
                  </div>
                  <div class="form-actions">
                    <button type="submit" class="btn-submit">Submit Application</button>
                  </div>
                </form>
              </div>
            </div>
            <div v-if="store.user && store.user.role === 'HRMgr'" class="hr-actions-card">
              <div class="card-header">
                <h2 class="form-title">HR Dashboard</h2>
              </div>
              <div class="card-body">
                <button @click="closeJob" class="btn-close">Close Job Posting</button>
                <button @click="filterCandidates" class="btn-filter">Filter Candidates</button>
                <div v-if="filterStatus" class="submission-status">
                  <p>{{ filterStatus }}</p>
                </div>
                <div v-if="closeJobStatus" class="submission-status">
                  <p>{{ closeJobStatus }}</p>
                </div>
              </div>
            </div>
            <div v-if="filteredCandidates.length > 0" class="filtered-candidates-card">
              <div class="card-header">
                <h2 class="form-title">Filtered Candidates: </h2>
              </div>
              <div class="card-body">
                <ul>
                  <li v-for="candidate in filteredCandidates" :key="candidate.email" class="candidate-item">
                    <p><strong>Name:</strong> {{ candidate.name }}</p>
                    <p><strong>Email:</strong> {{ candidate.email }}</p>
                    <p><strong>Score:</strong> {{ candidate.score }}</p>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="no-job-selected">
          <p>Select a job to view details and apply.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { store } from '../store.js';

const jobs = ref([]);
const selectedJob = ref(null);
const applicantName = ref('');
const applicantEmail = ref('');
const resumeFile = ref(null);
const submissionStatus = ref('');
const filterStatus = ref('');
const closeJobStatus = ref('');
const filteredCandidates = ref([]);

onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5002/jobs');
    jobs.value = response.data;
  } catch (error) {
    console.error('Error fetching jobs:', error);
  }
});

const selectJob = (job) => {
  selectedJob.value = job;
  if (store.user) {
    applicantName.value = store.user.displayName || '';
    applicantEmail.value = store.user.email || '';
  } else {
    applicantName.value = '';
    applicantEmail.value = '';
  }
  resumeFile.value = null;
  submissionStatus.value = '';
  filterStatus.value = '';
  closeJobStatus.value = '';
  filteredCandidates.value = [];
  const resumeInput = document.getElementById('resume');
  if(resumeInput) resumeInput.value = '';
};

const handleFileChange = (event) => {
  resumeFile.value = event.target.files[0];
};

const submitApplication = async () => {
  if (!selectedJob.value || !applicantName.value || !applicantEmail.value || !resumeFile.value) {
    submissionStatus.value = 'Please fill out all fields and select a resume.';
    return;
  }

  const formData = new FormData();
  formData.append('name', applicantName.value);
  formData.append('email', applicantEmail.value);
  formData.append('file', resumeFile.value);
  formData.append('job_id', selectedJob.value.job_id);

  submissionStatus.value = 'Submitting...';

  try {
    const response = await axios.post(`http://127.0.0.1:5002/applicationform`, formData);
    submissionStatus.value = 'Application submitted successfully!';
    applicantName.value = '';
    applicantEmail.value = '';
    resumeFile.value = null;
    document.getElementById('resume').value = '';

  } catch (error) {
    console.error('Error submitting application:', error);
    submissionStatus.value = `Error: ${error.response?.data?.error || 'An unexpected error occurred.'}`;
  }
};

const filterCandidates = async () => {
  if (!selectedJob.value) {
    filterStatus.value = 'Please select a job to filter candidates.';
    return;
  }
  filterStatus.value = 'Filtering candidates...';
  try {
    const response = await axios.get(`http://127.0.0.1:5002/jobs/${selectedJob.value.job_id}/candidates?min_score=60`);
    filteredCandidates.value = response.data;
    filterStatus.value = `Found ${response.data.length} candidates.`;
  } catch (error) {
    console.error('Error filtering candidates:', error);
    filterStatus.value = `Error: ${error.response?.data?.error || 'An unexpected error occurred.'}`;
    filteredCandidates.value = [];
  }
};

const closeJob = async () => {
  if (!selectedJob.value) {
    closeJobStatus.value = 'Please select a job to close.';
    return;
  }
  closeJobStatus.value = 'Closing job...';
  try {
    const response = await axios.delete(`http://127.0.0.1:5002/jobs/${selectedJob.value.job_id}`);
    closeJobStatus.value = response.data.message || 'Job closed successfully!';
    const jobsResponse = await axios.get('http://127.0.0.1:5002/jobs');
    jobs.value = jobsResponse.data;
    selectedJob.value = null;
  } catch (error) {
    console.error('Error closing job:', error);
    closeJobStatus.value = `Error: ${error.response?.data?.error || 'An unexpected error occurred.'}`;
  }
};
</script>

<style scoped>
.page-container {
  background-color: #f4f6f8;
  font-family: 'Poppins', sans-serif;
  width: 100%;
}

.page-header {
  padding: 40px;
  border-bottom: 1px solid #ddd;
}

.main-title {
  text-align: center;
  font-size: 2.5em;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 20px 0;
}

.button-container {
  text-align: right;
}

.job-listing-page {
  display: flex;
  height: calc(100vh - 180px); /* Adjust height based on header */
}

.job-list-container {
  width: 30%;
  padding: 20px;
  overflow-y: auto;
  border-right: 1px solid #ddd;
}

.job-details-container {
  width: 70%;
  padding: 40px;
  overflow-y: auto;
}

.btn-create {
  background: linear-gradient(135deg, #6e8efb, #a777e3);
  color: white;
  padding: 12px 25px;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1em;
  display: inline-block;
  box-shadow: 0 8px 25px rgba(110, 142, 251, 0.4);
  transition: all 0.3s ease;
}

.btn-create:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(110, 142, 251, 0.6);
}

.no-jobs {
  text-align: center;
  margin-top: 50px;
}

.no-jobs p {
  font-size: 1.2em;
  color: #7f8c8d;
}

.job-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.job-card {
  background: white;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.job-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
}

.job-card h2 {
  font-size: 1.5em;
  font-weight: 600;
  color: #34495e;
  margin-bottom: 5px;
}

.job-id {
  font-size: 0.8em;
  color: #95a5a6;
  font-family: 'Roboto Mono', monospace;
  margin-bottom: 15px;
}

.job-card p {
  color: #555;
  font-size: 1em;
  line-height: 1.5;
}

.no-job-selected {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
}

.no-job-selected p {
  font-size: 1.5em;
  color: #7f8c8d;
}

.job-details-card, .application-form-card, .hr-actions-card, .filtered-candidates-card {
  width: 100%;
  max-width: 800px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  margin: 0 auto 20px;
}

.card-header {
  padding: 30px;
  background: linear-gradient(135deg, #6e8efb, #a777e3);
  color: #fff;
}

.job-title {
  font-size: 2.5em;
  font-weight: 700;
  margin: 0;
}

.card-body {
  padding: 30px;
}

.job-description {
  font-size: 1.2em;
  line-height: 1.7;
  color: #555;
  margin-bottom: 30px;
}

.form-title {
  font-size: 2em;
  font-weight: 600;
  margin: 0;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.form-group input {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 1em;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #6e8efb;
  box-shadow: 0 0 0 3px rgba(110, 142, 251, 0.2);
}

.form-actions {
  text-align: right;
  margin-top: 20px;
}

.btn-submit {
  background: linear-gradient(135deg, #6e8efb, #a777e3);
  color: white;
  padding: 15px 35px;
  border: none;
  border-radius: 50px;
  font-weight: 600;
  font-size: 1.1em;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(110, 142, 251, 0.3);
  transition: all 0.3s ease;
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(110, 142, 251, 0.5);
}

.submission-status {
  margin-top: 20px;
  padding: 15px;
  border-radius: 10px;
  background-color: #eaf6ff;
  color: #2c3e50;
  text-align: center;
}

.hr-actions-card .card-body {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

.btn-close {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  padding: 15px 35px;
  border: none;
  border-radius: 50px;
  font-weight: 600;
  font-size: 1.1em;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(231, 76, 60, 0.3);
  transition: all 0.3s ease;
}

.btn-close:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(231, 76, 60, 0.5);
}

.btn-filter {
  background: linear-gradient(135deg, #fbbc05, #f29900); /* Google Yellow/Orange */
  color: white;
  padding: 15px 35px;
  border: none;
  border-radius: 50px;
  font-weight: 600;
  font-size: 1.1em;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(251, 188, 5, 0.3);
  transition: all 0.3s ease;
}

.btn-filter:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(251, 188, 5, 0.5);
}

.candidate-item {
  list-style-type: none;
  padding: 10px;
  border-bottom: 1px solid #eee;
}
</style>