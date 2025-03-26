<template>
    <div class="login-view">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-12 col-sm-8 col-md-6 col-lg-5">
                    <div class="card shadow-sm">
                        <div class="card-body">
                            <h1 class="text-center mb-4">Login</h1>
                            <form @submit.prevent="handleLogin">
                                <fieldset :disabled="loading">
                                    <div class="mb-3">
                                        <label for="email" class="form-label">Email Address</label>
                                        <input type="email" class="form-control" id="email" v-model.trim="email"
                                            required @focus="authStore.clearError('email')">
                                        <div v-if="errors.email" class="text-danger" aria-live="polite">
                                            {{ errors.email }}
                                        </div>
                                    </div>

                                    <div class="mb-3">
                                        <label for="password" class="form-label">Password</label>
                                        <input type="password" class="form-control" id="password" v-model="password"
                                            required @focus="authStore.clearError('password')">
                                        <div v-if="errors.password" class="text-danger" aria-live="polite">
                                            {{ errors.password }}
                                        </div>
                                    </div>

                                    <button type="submit" class="btn btn-primary w-100">
                                        <span v-if="loading" class="spinner-border spinner-border-sm" role="status"
                                            aria-hidden="true"></span>
                                        {{ loading ? 'Logging in...' : 'Login' }}
                                    </button>
                                </fieldset>
                            </form>

                            <div class="mt-3 text-center">
                                <p>Don't have an account? <router-link to="/register"
                                        class="fw-bold">Register</router-link></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const email = ref('');
const password = ref('');
const errors = ref({});
const loading = ref(false);

const validateForm = () => {
    errors.value = {};
    if (!email.value) errors.value.email = 'Email is required';
    if (!password.value) errors.value.password = 'Password is required';
    return Object.keys(errors.value).length === 0;
};

const handleLogin = async () => {
    if (!validateForm()) return;

    loading.value = true;
    try {
        await authStore.loginUser({ email: email.value, password: password.value });
    } catch (error) {
        console.error('Login error:', error);
    } finally {
        loading.value = false;
    }
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
}
</style>