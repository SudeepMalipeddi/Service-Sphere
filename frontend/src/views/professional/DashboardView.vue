<template>
    <div class="professional-dashboard">
        <div class="container-fluid">
            <!-- Profile Status Alerts -->
            <div v-if="profile">
                <div v-if="isProfilePending" class="alert alert-warning" role="alert">
                    <h4 class="alert-heading">Your profile is pending verification</h4>
                    <div v-if="!profile.documents_url || profile.documents_url.length === 0">
                        <p>Verification documents are required for approval.</p>
                        <p>Please upload your verification documents to get approved.</p>
                        <router-link to="/professional/profile" class="btn btn-primary">
                            Upload Documents
                        </router-link>
                    </div>
                    <div v-else>
                        <p>Thank you for submitting your documents. Your profile is currently under review.</p>
                        <p>You'll be notified once your profile is
                            verified.</p>
                    </div>
                </div>

                <div v-if="isProfileRejected" class="alert alert-danger" role="alert">
                    <h4 class="alert-heading">Your profile verification was rejected</h4>
                    <p>Reason: {{ profile.rejection_reason || 'No reason provided' }}</p>
                    <p>Please update your profile with the required information and submit again.</p>
                    <router-link to="/professional/profile" class="btn btn-primary">
                        Update Profile
                    </router-link>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center my-5">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3">Loading your dashboard...</p>
            </div>

            <div v-else-if="profile" class="dashboard-content">
                <!-- Welcome Banner -->
                <div class="row mb-4">
                    <div class="col-12">
                        <div class="card bg-primary text-white">
                            <div class="card-body d-flex align-items-center">
                                <div class="me-3">
                                    <div class="avatar-circle">
                                        {{ getInitials(profile.user.name) }}
                                    </div>
                                </div>
                                <div>
                                    <h2 class="card-title mb-1">Welcome, {{ profile.user.name }}!</h2>
                                    <p class="card-text mb-0">{{ profile.service_name || 'Professional Service' }}</p>
                                    <p class="small mb-0">
                                        <span :class="getStatusBadgeClass(profile.verification_status)">
                                            {{ formatStatus(profile.verification_status) }}
                                        </span>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Dashboard Grid -->
                <div class="row">
                    <!-- Stats Overview -->
                    <div class="col-md-8">
                        <div class="row">
                            <!-- Request Stats -->
                            <div class="col-md-4 mb-4">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <h5 class="text-muted">Active Requests</h5>
                                        <h2 class="display-4">{{ activeRequestsCount }}</h2>
                                        <small>Assigned to you</small>
                                    </div>
                                </div>
                            </div>

                            <div class="col-md-4 mb-4">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <h5 class="text-muted">Available</h5>
                                        <h2 class="display-4">{{ availableRequestsCount }}</h2>
                                        <small>Not yet assigned</small>
                                    </div>
                                </div>
                            </div>

                            <div class="col-md-4 mb-4">
                                <div class="card h-100">
                                    <div class="card-body text-center">
                                        <h5 class="text-muted">Completed</h5>
                                        <h2 class="display-4">{{ completedRequestsCount }}</h2>
                                        <small>Total completed jobs</small>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Recent Requests -->
                        <div class="card mb-4">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">Recent Requests</h5>
                                <router-link to="/professional/requests" class="btn btn-sm btn-outline-primary">View
                                    All</router-link>
                            </div>
                            <div class="card-body p-0">
                                <div v-if="requestStore.loading" class="text-center py-4">
                                    <div class="spinner-border spinner-border-sm" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                                <div v-else-if="recentRequests.length === 0" class="text-center py-4">
                                    <p class="mb-0">No recent requests found.</p>
                                </div>
                                <div v-else class="list-group list-group-flush">
                                    <div v-for="request in recentRequests" :key="request.id" class="list-group-item">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div>
                                                <h6 class="mb-1">{{ request.service_name }}</h6>
                                                <small class="text-muted">Customer: {{ request.customer_name }}</small>
                                                <small class="d-block text-muted">{{
                                                    formatDateTime(request.scheduled_date) }}</small>
                                            </div>
                                            <div class="d-flex align-items-center">
                                                <span :class="getStatusBadgeClass(request.status)" class="me-2">
                                                    {{ request.status }}
                                                </span>
                                                <router-link :to="`/professional/requests?id=${request.id}`"
                                                    class="btn btn-sm btn-outline-secondary">
                                                    Details
                                                </router-link>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Sidebar -->
                    <div class="col-md-4">
                        <!-- Notifications -->
                        <div class="card mb-4">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">Notifications</h5>
                                <span v-if="notificationStore.unreadCount > 0" class="badge bg-danger">{{
                                    notificationStore.unreadCount }}</span>
                            </div>
                            <div class="card-body p-0">
                                <div v-if="notificationStore.loading" class="text-center py-4">
                                    <div class="spinner-border spinner-border-sm" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                                <div v-else-if="notificationStore.unreadNotifications.length === 0"
                                    class="text-center py-4">
                                    <p class="mb-0">No new notifications.</p>
                                </div>
                                <div v-else class="list-group list-group-flush">
                                    <div v-for="notification in notificationStore.unreadNotifications.slice(0, 5)"
                                        :key="notification.id" @click="markAsRead(notification.id)"
                                        class="list-group-item list-group-item-action">
                                        <div class="d-flex">
                                            <div class="notification-icon me-2">
                                                <i class="bi bi-bell-fill"
                                                    v-if="notification.type === 'new_request'"></i>
                                                <i class="bi bi-chat-dots-fill"
                                                    v-else-if="notification.type === 'review_received'"></i>
                                                <i class="bi bi-info-circle-fill" v-else></i>
                                            </div>
                                            <div>
                                                <p class="mb-1">{{ notification.message }}</p>
                                                <small class="text-muted">{{ formatDateTime(notification.created_at)
                                                    }}</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-if="notificationStore.unreadNotifications.length > 5"
                                        class="p-2 text-center">
                                        <router-link to="/notifications" class="btn btn-sm btn-link">
                                            View all notifications
                                        </router-link>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Reviews Summary -->
                        <div class="card mb-4">
                            <div class="card-header">
                                <h5 class="mb-0">Your Ratings</h5>
                            </div>
                            <div class="card-body">
                                <div v-if="reviewsLoading" class="text-center">
                                    <div class="spinner-border spinner-border-sm" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                                <div v-else-if="reviewsCount === 0" class="text-center">
                                    <p>No reviews yet. Complete services to get reviews.</p>
                                </div>
                                <div v-else>
                                    <div class="d-flex align-items-center mb-3">
                                        <h2 class="mb-0 me-2">{{ averageRating.toFixed(1) }}</h2>
                                        <div class="star-rating">
                                            <span v-for="i in 5" :key="i"
                                                :class="{ 'filled': i <= Math.round(averageRating) }">★</span>
                                        </div>
                                        <span class="ms-2 text-muted">({{ reviewsCount }} reviews)</span>
                                    </div>

                                    <div v-if="recentReviews.length > 0">
                                        <h6>Recent Reviews:</h6>
                                        <div v-for="review in recentReviews" :key="review.id"
                                            class="recent-review mb-3">
                                            <div class="d-flex align-items-center mb-1">
                                                <div class="star-rating small">
                                                    <span v-for="i in 5" :key="i"
                                                        :class="{ 'filled': i <= review.rating }">★</span>
                                                </div>
                                                <small class="ms-2 text-muted">{{ formatDate(review.created_at)
                                                    }}</small>
                                            </div>
                                            <p class="mb-0 small">{{ review.comment || 'No comment provided' }}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Service Overview (if professional has a service) -->
                        <div v-if="profile.service_id" class="card mb-4">
                            <div class="card-header">
                                <h5 class="mb-0">Your Service</h5>
                            </div>
                            <div class="card-body">
                                <div v-if="serviceStore.loading" class="text-center">
                                    <div class="spinner-border spinner-border-sm" role="status">
                                        <span class="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                                <div v-else-if="currentService">
                                    <h6>{{ currentService.name }}</h6>
                                    <p class="small">{{ currentService.description }}</p>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <span class="fw-bold">{{ formatPrice(currentService.base_price) }}</span>
                                        <span
                                            :class="currentService.is_active ? 'badge bg-success' : 'badge bg-danger'">
                                            {{ currentService.is_active ? 'Active' : 'Inactive' }}
                                        </span>
                                    </div>
                                </div>
                                <div v-else class="text-center">
                                    <p>Service information not available.</p>
                                </div>
                            </div>
                        </div>

                        <!-- Quick Actions -->
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Quick Actions</h5>
                            </div>
                            <div class="card-body">
                                <div class="d-grid gap-2">
                                    <router-link to="/professional/requests?available=true" class="btn btn-primary">
                                        Browse Available Requests
                                    </router-link>
                                    <router-link to="/professional/requests" class="btn btn-outline-primary">
                                        Manage My Requests
                                    </router-link>
                                    <router-link to="/professional/profile" class="btn btn-outline-secondary">
                                        Edit Profile
                                    </router-link>
                                    <router-link to="/professional/requests?tab=rejected"
                                        class="btn btn-outline-secondary">
                                        View Rejected Requests
                                    </router-link>
                                    <button v-if="notificationStore.unreadCount > 0" @click="markAllNotificationsAsRead"
                                        class="btn btn-outline-secondary" :disabled="notificationStore.loading">
                                        Mark All Notifications As Read
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getProfessional } from '@/api/professional';
import { getUser } from '@/utils/authutils';
import { formatDateTime, formatDate, formatPrice } from '@/utils/formatters';
import { useRequestStore } from '@/stores/requests';
import { useNotificationsStore } from '@/stores/notifications';
import { useServiceStore } from '@/stores/services';
import api from '@/api';

// Initialize stores
const requestStore = useRequestStore();
const notificationStore = useNotificationsStore();
const serviceStore = useServiceStore();

// Local state
const profile = ref(null);
const loading = ref(true);
const recentReviews = ref([]);
const reviewsLoading = ref(false);
const reviewsCount = ref(0);
const averageRating = ref(0);


const isProfilePending = computed(() => profile.value?.verification_status === 'pending');
const isProfileRejected = computed(() => profile.value?.verification_status === 'rejected');


const recentRequests = computed(() => {
    return requestStore.requests.slice(0, 5);
});

const activeRequestsCount = computed(() => {
    return requestStore.requests.filter(req => req.status === 'assigned').length;
});

const availableRequestsCount = computed(() => {
    return requestStore.availableRequests.length;
});

const completedRequestsCount = computed(() => {
    return requestStore.requests.filter(req => ['completed', 'closed'].includes(req.status)).length;
});


const currentService = computed(() => {
    if (!profile.value?.service_id) return null;
    return serviceStore.serviceById(profile.value.service_id);
});

const formatStatus = (status) => {
    switch (status) {
        case 'approved': return 'Verified';
        case 'pending': return 'Pending Verification';
        case 'rejected': return 'Verification Rejected';
        default: return status;
    }
};

const getInitials = (name) => {
    if (!name) return '';
    return name.split(' ')
        .map(word => word.charAt(0).toUpperCase())
        .join('')
        .substring(0, 2);
};

const getStatusBadgeClass = (status) => {
    switch (status) {
        case 'approved': return 'badge bg-success';
        case 'pending': return 'badge bg-warning text-dark';
        case 'rejected': return 'badge bg-danger';
        case 'assigned': return 'badge bg-warning text-dark';
        case 'completed': return 'badge bg-primary';
        case 'closed': return 'badge bg-success';
        case 'requested': return 'badge bg-info';
        case 'cancelled': return 'badge bg-danger';
        default: return 'badge bg-secondary';
    }
};

// Notification actions
const markAsRead = async (notificationId) => {
    try {
        await notificationStore.markNotificationAsRead(notificationId);
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
};

const markAllNotificationsAsRead = async () => {
    try {
        await notificationStore.markAllNotificationsAsRead();
    } catch (error) {
        console.error('Error marking all notifications as read:', error);
    }
};

// Fetch professional data
const fetchProfessionalData = async () => {
    loading.value = true;
    try {
        const user = await getUser();
        if (user?.id && user.role === 'professional') {
            const professionalId = user.professional_id;

            if (professionalId) {
                const response = await getProfessional(professionalId);
                profile.value = response.data.professional;

                // Fetch other data using stores
                await Promise.all([
                    fetchReviews(),
                    requestStore.fetchRequests(),
                    requestStore.fetchAvailableRequests(),
                    notificationStore.fetchNotifications(),
                    serviceStore.fetchServices()
                ]);
            }
        }
    } catch (err) {
        console.error("Failed to fetch profile:", err);
    } finally {
        loading.value = false;
    }
};

// Fetch reviews for the professional
const fetchReviews = async () => {
    reviewsLoading.value = true;
    try {
        if (!profile.value?.id) return;

        const professionalId = profile.value.id;
        const response = await api.get('/reviews', {
            params: { professional_id: professionalId },
        });

        const reviews = response.data.reviews;

        if (reviews.length > 0) {
            const totalRating = reviews.reduce((sum, review) => sum + review.rating, 0);
            averageRating.value = totalRating / reviews.length;
            reviewsCount.value = reviews.length;

            recentReviews.value = reviews
                .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                .slice(0, 3);
        }
    } catch (error) {
        console.error('Error fetching reviews:', error);
    } finally {
        reviewsLoading.value = false;
    }
};

onMounted(() => {
    fetchProfessionalData();
});
</script>

<style scoped>
.avatar-circle {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: 500;
}

.star-rating {
    display: inline-block;
}

.star-rating span {
    font-size: 18px;
    color: #ccc;
    padding: 0 2px;
}

.star-rating.small span {
    font-size: 14px;
}

.star-rating span.filled {
    color: #ffc107;
}

.notification-icon {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #007bff;
}

.recent-review {
    padding-bottom: 10px;
    border-bottom: 1px solid #e9ecef;
}

.recent-review:last-child {
    border-bottom: none;
}
</style>