import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

// Configure axios to send credentials (cookies) with requests
axios.defaults.withCredentials = true;

export const authApi = {
  // Get current user profile
  getProfile: async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auth/profile`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        return { success: false, authenticated: false };
      }
      throw error;
    }
  },

  // Check authentication status
  getStatus: async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auth/status`);
      return response.data;
    } catch (error) {
      return { authenticated: false, user: null };
    }
  },

  // Logout
  logout: async () => {
    const response = await axios.post(`${API_URL}/api/auth/logout`);
    return response.data;
  },

  // Get Google OAuth URL (redirects to Google)
  loginWithGoogle: () => {
    window.location.href = `${API_URL}/api/auth/google`;
  },
};

