<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container">
            <router-link class="navbar-brand" to="/">Service Sphere</router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <template v-if="isAdmin && isAuthenticated">
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


                    <template v-if="isCustomer && isAuthenticated">
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
                            <router-link class="nav-link" to="/customer/profile">My Profile</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/customer/reviews">My Reviews</router-link>
                        </li>
                    </template>


                    <template v-if="isProfessional && isAuthenticated">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/professional">Dashboard</router-link>
                        </li>
                        <li class="nav-item">
                            <router-link class="nav-link" to="/professional/profile">My Profile</router-link>
                        </li>
                        <li class="nav-item" v-if="isProfilePending">
                            <span class="nav-link text-danger">Profile Pending Verification</span>
                        </li>
                        <li class="nav-item" v-if="!isProfilePending">
                            <router-link class="nav-link" to="/professional/requests">Requests</router-link>
                        </li>
                    </template>
                </ul>
                <ul class="navbar-nav">

                    <li class="nav-item dropdown" v-if="isAuthenticated && authStore.user">
                        <a class="nav-link dropdown-toggle position-relative" href="#" id="notificationsDropdown"
                            role="button" data-bs-toggle="dropdown">
                            <i class="bi bi-bell"></i>
                            <span v-if="unreadCount > 0"
                                class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                                {{ unreadCount > 9 ? '9+' : unreadCount }}
                            </span>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li v-if="notificationsLoading" class="text-center p-3">
                                <div class="spinner-border spinner-border-sm" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </li>

                            <li v-else-if="!notifications.length" class="dropdown-item text-center">
                                No notifications
                            </li>

                            <template v-else>
                                <li v-for="notification in notifications.slice(0, 5)" :key="notification.id">
                                    <a class="dropdown-item" href="#" :class="{ 'bg-light': !notification.is_read }"
                                        @click.prevent="markAsRead(notification.id)">
                                        <small class="text-muted d-block">{{ formatDate(notification.created_at)
                                            }}</small>
                                        {{ notification.message }}
                                    </a>
                                </li>
                                <li>
                                    <hr class="dropdown-divider">
                                </li>
                                <li>
                                    <router-link class="dropdown-item text-center" to="/notifications">
                                        View All
                                    </router-link>
                                </li>
                            </template>
                        </ul>
                    </li>


                    <li class="nav-item dropdown" v-if="isAuthenticated && userName && authStore.user">
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


                    <template v-if="!isAuthenticated">
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
import { useNotificationsStore } from '@/stores/notifications';
import { storeToRefs } from 'pinia';
import { computed, onMounted, ref, watchEffect, watch } from 'vue';
import { formatDate } from '@/utils/formatters';
import { getProfessional } from '@/api/professional';

const authStore = useAuthStore();
const notificationStore = useNotificationsStore();
const { notifications, unreadCount, notificationsLoading } = storeToRefs(useNotificationsStore());

const isAuthenticated = computed(() => authStore.isAuthenticated);
const userRole = computed(() => authStore.userRole);
const userName = computed(() => authStore.userName);
const isAdmin = computed(() => authStore.isAdmin);
const isCustomer = computed(() => authStore.isCustomer);
const isProfessional = computed(() => authStore.isProfessional);
const isProfilePending = ref(false);
const user = computed(() => authStore.user);
const professionalId = computed(() => user.value?.professional_id);

const fetchProfileStatus = async () => {
    if (isAuthenticated.value && isProfessional.value && professionalId.value) {
        try {
            const profile = await getProfessional(professionalId.value);
            isProfilePending.value = profile.verification_status === 'pending';
        } catch (error) {
            console.error('Error fetching professional profile:', error);
            isProfilePending.value = false;
        }
    }
};

const fetchUserData = () => {
    if (isAuthenticated.value && authStore.token && authStore.user) {
        notificationStore.fetchNotifications({ limit: 5 });

        if (isProfessional.value && professionalId.value) {
            fetchProfileStatus();
        }
    }
};

const logout = async () => {
    await authStore.logoutUser();
    router.push('/');
};

const markAsRead = (id) => {
    notificationStore.markNotificationAsRead(id);
};

watchEffect(() => {
    const authenticated = isAuthenticated.value;
    const token = authStore.token;
    const userExists = !!authStore.user;

    if (authenticated && token && userExists) {
        fetchUserData();
    }
});

watch(() => authStore.isAuthenticated, (newValue, oldValue) => {
    if (newValue === true && oldValue === false) {
        console.log('User just logged in, updating navbar');
        fetchUserData();
    }
});

watch(() => authStore.user, (newUser) => {
    if (newUser && isAuthenticated.value) {
        fetchUserData();
    }
}, { deep: true });

onMounted(() => {
    if (isAuthenticated.value && authStore.token && authStore.user) {
        fetchUserData();
    }
});
</script>