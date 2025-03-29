<template>
    <div class="login-view">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-12 col-sm-8 col-md-6 col-lg-5">
                    <div class="card shadow">
                        <div class="card-body p-4">
                            <h1 class="text-center mb-4">Login</h1>

                            <!-- Alert messages -->
                            <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show"
                                role="alert">
                                {{ errorMessage }}
                                <button type="button" class="btn-close" @click="authStore.clearError()"></button>
                            </div>
                            <div v-if="successMessage" class="alert alert-success alert-dismissible fade show"
                                role="alert">
                                {{ successMessage }}
                                <button type="button" class="btn-close" @click="clearSuccess"></button>
                            </div>

                            <form @submit.prevent="handleLogin">
                                <fieldset :disabled="loading">
                                    <div class="mb-3">
                                        <label for="email" class="form-label">Email Address</label>
                                        <input type="email" class="form-control" id="email" v-model.trim="email"
                                            required @focus="authStore.clearError('email')">
                                        <div v-if="errors.email" class="text-danger mt-1 small" aria-live="polite">
                                            {{ errors.email }}
                                        </div>
                                    </div>

                                    <div class="mb-3">
                                        <label for="password" class="form-label">Password</label>
                                        <input type="password" class="form-control" id="password" v-model="password"
                                            required @focus="authStore.clearError('password')">
                                        <div v-if="errors.password" class="text-danger mt-1 small" aria-live="polite">
                                            {{ errors.password }}
                                        </div>
                                    </div>

                                    <button type="submit" class="btn btn-primary w-100 py-2">
                                        <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"
                                            aria-hidden="true"></span>
                                        {{ loading ? 'Logging in...' : 'Login' }}
                                    </button>
                                </fieldset>
                            </form>

                            <div class="mt-4 text-center">
                                <p class="mb-0">Don't have an account? <router-link to="/register"
                                        class="fw-bold text-decoration-none">Register</router-link></p>
                            </div>
                        </div>
                    </div>
                    <div>
                        <router-link to="/" class="btn btn-link text-decoration-none">
                            <i class="bi bi-arrow-left"></i> Back to Home
                        </router-link>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const email = ref('');
const password = ref('');
const errors = ref({});
const loading = ref(false);
const errorMessage = computed(() => authStore.errorMessage);
const successMessage = ref('');

const validateForm = () => {
    errors.value = {};
    if (!email.value) errors.value.email = 'Email is required';
    if (!password.value) errors.value.password = 'Password is required';
    return Object.keys(errors.value).length === 0;
};

const handleLogin = async () => {
    if (!validateForm()) return;

    // Clear any previous messages
    authStore.clearError();
    successMessage.value = '';

    loading.value = true;
    try {
        await authStore.loginUser({ email: email.value, password: password.value });
        successMessage.value = 'Login successful! Redirecting...';
    } catch (error) {
        console.error('Login error:', error);
        // No need to set errorMessage here as it should be set in the store's loginUser method on failure
    } finally {
        loading.value = false;
    }
};

const clearSuccess = () => {
    successMessage.value = '';
};
</script>

<style scoped>
.login-view {
    width: 100%;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f8f9fa;
    padding: 2rem;
}

.card {
    width: 100%;
    max-width: 500px;
    border-radius: 10px;
    border: none;
}

.btn-primary {
    font-weight: 500;
    letter-spacing: 0.5px;
}

.alert {
    margin-bottom: 20px;
}
</style>