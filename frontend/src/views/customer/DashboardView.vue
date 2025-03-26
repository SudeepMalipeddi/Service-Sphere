<template>
    <div class="customer-dashboard">
        <h1>My Dashboard</h1>

        <div class="row mb-4">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Welcome, {{ userName }}!</h5>
                        <p class="card-text">Use the dashboard to manage your service requests and reviews.</p>

                        <div class="d-grid gap-2 d-md-flex justify-content-md-start">
                            <router-link to="/customer/services" class="btn btn-primary">Browse Services</router-link>
                            <router-link to="/customer/requests" class="btn btn-outline-primary">My
                                Requests</router-link>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card bg-light">
                    <div class="card-body">
                        <h5 class="card-title">Notifications</h5>
                        <div v-if="loading" class="text-center p-3">
                            <div class="spinner-border spinner-border-sm" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>

                        <div v-else-if="!notifications.length" class="text-center p-3">
                            <p class="mb-0">No new notifications</p>
                        </div>

                        <div v-else class="list-group list-group-flush">
                            <div v-for="notification in notifications.slice(0, 3)" :key="notification.id"
                                class="list-group-item" :class="{ 'bg-light': !notification.is_read }">
                                <div class="d-flex justify-content-between align-items-center">
                                    <small class="text-muted">{{ formatDate(notification.created_at) }}</small>
                                    <button v-if="!notification.is_read" class="btn btn-sm btn-link p-0"
                                        @click="markNotificationAsRead(notification.id)">Mark read</button>
                                </div>
                                <p class="mb-0">{{ notification.message }}</p>
                            </div>
                        </div>

                        <div class="text-center mt-3" v-if="notifications.length > 3">
                            <router-link to="/notifications" class="btn btn-sm btn-outline-secondary">View
                                All</router-link>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Quick Actions</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-6 col-md-3 mb-2">
                        <router-link to="/customer/services"
                            class="btn btn-outline-primary w-100 d-flex align-items-center justify-content-center">
                            <i class="bi bi-search me-2"></i> Find Services
                        </router-link>
                    </div>
                    <div class="col-6 col-md-3 mb-2">
                        <router-link to="/customer/requests"
                            class="btn btn-outline-primary w-100 d-flex align-items-center justify-content-center">
                            <i class="bi bi-clipboard-check me-2"></i> My Requests
                        </router-link>
                    </div>
                    <div class="col-6 col-md-3 mb-2">
                        <router-link to="/customer/reviews"
                            class="btn btn-outline-primary w-100 d-flex align-items-center justify-content-center">
                            <i class="bi bi-star me-2"></i> My Reviews
                        </router-link>
                    </div>
                    <div class="col-6 col-md-3 mb-2">
                        <router-link to="/customer/profile"
                            class="btn btn-outline-primary w-100 d-flex align-items-center justify-content-center">
                            <i class="bi bi-person me-2"></i> My Profile
                        </router-link>
                    </div>
                </div>
            </div>
        </div>

        <div class="card" v-if="recentRequests.length">
            <div class="card-header">
                <h5 class="mb-0">Recent Requests</h5>
            </div>
            <div class="list-group list-group-flush">
                <router-link v-for="request in recentRequests.slice(0, 3)" :key="request.id" :to="`/customer/requests/`"
                    class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">{{ request.service_name }}</h6>
                        <small>{{ formatDate(request.scheduled_date) }}</small>
                    </div>
                    <div class="d-flex justify-content-between">
                        <small class="text-muted">Status: {{ request.status.replace('_', ' ') }}</small>
                    </div>
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { storeToRefs } from 'pinia';

import { formatDate, formatPrice, truncate } from '@/utils/formatters';
import { useAuthStore } from '@/stores/auth';
import { useRequestStore } from '@/stores/requests';
import { useNotificationsStore } from '@/stores/notifications';
import { useServiceStore } from '@/stores/services';

const authStore = useAuthStore();
const requestStore = useRequestStore();
const serviceStore = useServiceStore();
const notificationStore = useNotificationsStore();

const { userName } = storeToRefs(authStore);
const { requests, loading: requestsLoading } = storeToRefs(requestStore);
const { services, loading: servicesLoading } = storeToRefs(serviceStore);
const { notifications, loading } = storeToRefs(notificationStore);

const recentRequests = computed(() => requests.value.slice(0, 5));

const markNotificationAsRead = async (id) => {
    try {
        await notificationStore.markNotificationAsRead(id);
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
};

onMounted(() => {
    requestStore.fetchRequests();
    serviceStore.fetchServices();
    notificationStore.fetchNotifications();
});
</script>