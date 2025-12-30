<template>
  <div class="contact-us-container">
    <h1>Contact Us</h1>
    <div class="card-container">
      <div class="card">
        <img src="..\assets\abhishek.jpg" alt="Team Member 1" class="profile-pic">
        <div class="info">
          <p class="name">Abhishek Darji</p>
          <p class="roll">ID: 019113471</p>
          <p class="email">abhishek.darji@sjsu.edu</p>
        </div>
      </div>
      <div class="card">
        <img src="..\assets\aniket.jpg" alt="Team Member 2" class="profile-pic">
        <div class="info">
          <p class="name">Aniket Naik</p>
          <p class="roll">ID: 019107114</p>
          <p class="email">aniketanil.naik@sjsu.edu</p>
        </div>
      </div>
      <div class="card">
        <img src="..\assets\shilpa.jpg" alt="Team Member 3" class="profile-pic">
        <div class="info">
          <p class="name">Shilpa Yelkur Ramakrishnaiah</p>
          <p class="roll">ID: 019151782</p>
          <p class="email">shilpa.ramakrishna@sjsu.edu</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.contact-us-container {
  text-align: center;
  padding: 2rem;
}
.card-container {
  display: flex;
  justify-content: space-around;
  margin-top: 2rem;
  flex-wrap: wrap; /* Allows cards to wrap on smaller screens */
}
.card {
  width: 300px;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  text-align: center;
}
.profile-pic {
  width: 200px;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
}
.info {
  margin-top: 1rem;
}
.name {
  font-weight: bold;
  font-size: 1.2rem;
}
.roll, .email {
  color: #555;
  font-size: 0.9rem;
}
</style>
