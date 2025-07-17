import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'https://api.ischool.ng/api/teachers/', // base path for teacher-related API endpoints
  headers: {
    'Content-Type': 'application/json',
  },
});

  axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    // ✅ Skip attaching token for login endpoint
    const isLoginRequest = config.url?.endsWith("login/");

    if (token && !isLoginRequest) {
      config.headers["Authorization"] = `Token ${token}`;
    } else {
      delete config.headers["Authorization"]; // 🧼 Clean header if no token or login request
    }

    return config;
  },
  (error) => Promise.reject(error)
);

export default axiosInstance;
