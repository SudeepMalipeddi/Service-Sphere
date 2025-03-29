import axios from 'axios';
import { getToken, clearAuth } from '@/utils/authutils';

const api = axios.create({
    baseURL: 'http://localhost:5000/api',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
})

api.interceptors.request.use(
    config => {
        const token = getToken();
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    error => Promise.reject(error)
)

api.interceptors.response.use(
    response => {
        // Handle successful responses
        return response;
    },
    error => {
        // Handle errors
        if (error.response.status === 401) {
            clearAuth();
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
)


export default api;