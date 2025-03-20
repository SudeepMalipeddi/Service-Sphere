import { defineStore } from "pinia";
import { login, register, refreshToken } from "@/api/auth";
import { setAuth, clearAuth, getToken, getUser, getRefreshToken } from "@/utils/authutils";
import router from "@/router";
import axios from "axios";

export const useAuthStore = defineStore('auth', {
    state: () => {
        const user = getUser();
        return {
            user: user,
            isAuthenticated: !!user?.role,
            loading: false,
            errorMessage: null,
            successMessage: null
        }
    },

    getters: {
        userRole: (state) => state.user.role || null,
        userName: (state) => state.user.name || '',
        isAdmin: (state) => state.user?.role === 'admin',
        isCustomer: (state) => state.user?.role === 'customer',
        isProfessional: (state) => state.user?.role === 'professional'
    },
    actions: {
        async loginUser(credentials) {
            this.loading = true;
            this.errorMessage = null;

            try {
                const response = await login(credentials);
                setAuth({
                    access_token: response.data.access_token,
                    refresh_token: response.data.refresh_token,
                    user: response.data.user
                })

                this.user = response.data.user
                this.isAuthenticated = true
                this.successMessage = 'Login successful'


                if (this.user.role === 'admin') {
                    router.push('/admin')
                }

                return response
            } catch (error) {
                this.errorMessage = error.response?.data?.message || 'Login failed'
                throw error
            } finally {
                this.loading = false
            }
        },
        async registerUser(userData) {
            this.loading = true
            this.errorMessage = null

            try {
                const response = await register(userData)

                // Store auth data
                setAuth({
                    access_token: response.data.access_token,
                    refresh_token: response.data.refresh_token,
                    user: response.data.user
                })

                // Update state
                this.user = response.data.user
                this.isAuthenticated = true
                this.successMessage = 'Registration successful'

                if (this.user.role === 'customer') {
                    router.push('/customer')
                } else if (this.user.role === 'professional') {
                    router.push('/professional')
                } else {
                    router.push('/')
                }

                return response
            } catch (error) {
                this.errorMessage = error.response?.data?.message || 'Registration failed'
                throw error
            } finally {
                this.loading = false
            }
        },
        async refreshToken() {
            const refresh = getRefreshToken();

            if (!refresh) {
                this.logoutUser();
                return;
            }
            try {
                const response = await refreshToken(refresh);

                setAuth({
                    access_token: response.data.access_token,
                    refresh_token: refresh,
                    user: this.user
                })
                return response
            } catch (error) {
                console.error('Token refresh failed:', error)
                this.logoutUser()
            }
        },
        async logoutUser() {
            this.loading = true;
            const token = getToken();

            try {
                await axios.post('/logout', {}, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });

            } catch (error) {
                console.error('Logout request failed:', error.response?.data || error.message);
            } finally {
                // Clear authentication after the request is made
                clearAuth();
                this.user = null;
                this.isAuthenticated = false;
                this.loading = false;
                router.push('/login');
            }
        },

        clearError() {
            this.errorMessage = null
        },
        clearSuccess() {
            this.successMessage = null
        },
        checkAuth() {
            // const user = JSON.parse(localStorage.getItem('user')) || null;

            const user = getUser();
            if (user) {
                this.user = user
                this.isAuthenticated = true
            } else {
                this.user = null
                this.isAuthenticated = false
            }
        }
    }
})