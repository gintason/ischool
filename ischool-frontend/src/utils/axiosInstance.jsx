import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'https://www.ischool.ng/api/teachers/', // base path for teacher-related API endpoints
  headers: {
    'Content-Type': 'application/json',
  },
});

    axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");
        if (token) {
        config.headers["Authorization"] = `Token ${token}`;
        } else {
        delete config.headers["Authorization"]; // 🧼 Clean header if no token
        }
        return config;
    },
    (error) => Promise.reject(error)
    );

export default axiosInstance;
