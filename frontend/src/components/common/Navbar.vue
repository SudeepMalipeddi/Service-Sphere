<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <router-link class="navbar-brand" to="/">Service Sphere</router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <template v-if="isAdmin">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/admin">Dashboard</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/admin/professionals">Professionals</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/admin/customers">Customers</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/admin/services">Services</router-link>
                        </li>
                    </template>

                    <!-- Customer Navigation -->
                    <template v-if="isCustomer">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/customer">Dashboard</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/customer/services">Services</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/customer/requests">My Requests</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/customer/reviews">My Reviews</router-link>
                        </li>
                    </template>

                    <!-- Professional Navigation -->
                    <template v-if="isProfessional">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/professional">Dashboard</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/professional/requests">Requests</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/professional/profile">My Profile</router-link>
                        </li>
                    </template>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item dropdown" v-if="isAuthenticated">
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button"
                            data-bs-toggle="dropdown">
                            {{ userName }}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li>
                                <span class="dropdown-item-text text-muted">
                                    <small>{{ userRole }}</small>
                                </span>
                            </li>
                            <li>
                                <hr class="dropdown-divider">
                            </li>
                            <li>
                                <a class="dropdown-item" href="#" @click.prevent="logout">
                                    Logout
                                </a>
                            </li>
                        </ul>
                    </li>
                    <template v-else>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/login">Login</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/register">Register</router-link>
                        </li>
                    </template>
                </ul>
            </div>

        </div>
    </nav>
</template>


<script setup>

import router from '@/router';
import { useAuthStore } from '@/stores/auth';
import { computed, onMounted } from 'vue';

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated)
const userRole = computed(() => authStore.userRole)
const isAdmin = computed(() => authStore.isAdmin)
const isCustomer = computed(() => authStore.isCustomer)
const isProfessional = computed(() => authStore.isProfessional)

const logout = async () => {
    await authStore.logoutUser();
    router.push('/')
}

</script>