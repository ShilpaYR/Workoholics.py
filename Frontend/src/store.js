import { reactive } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export const store = reactive({
  user: null, // Will hold user data after login

  // Centralized logout function
  async logout() {
    const router = useRouter();
    try {
      await axios.post('http://localhost:5002/logout', {}, { withCredentials: true });
      this.user = null;
      // Redirect to the career page after successful logout
      if (router) {
        router.push('/career-page');
      } else {
        // Fallback for non-component usage
        window.location.href = '/career-page';
      }
    } catch (error) {
      console.error('Failed to log out:', error);
      // Even if the backend call fails, clear the frontend state as a fallback
      this.user = null;
      if (router) {
        router.push('/career-page');
      } else {
        window.location.href = '/career-page';
      }
    }
  }
});
