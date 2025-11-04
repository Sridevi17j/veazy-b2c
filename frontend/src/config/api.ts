/**
 * API Configuration
 * Centralized configuration for backend API URLs
 */

// Get backend URL from environment variable or fallback to localhost
export const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Export for convenience
export const API_CONFIG = {
  baseURL: BACKEND_URL,
  endpoints: {
    auth: {
      login: `${BACKEND_URL}/auth/login`,
      register: `${BACKEND_URL}/auth/register`,
      verifyOtp: `${BACKEND_URL}/auth/verify-otp`,
    },
    countries: `${BACKEND_URL}/countries`,
    threads: `${BACKEND_URL}/threads`,
    assistants: `${BACKEND_URL}/assistants`,
  },
};

// Helper function to get full endpoint URL
export const getEndpoint = (path: string): string => {
  return `${BACKEND_URL}${path.startsWith('/') ? path : `/${path}`}`;
};
