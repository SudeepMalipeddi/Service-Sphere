<template>
    <div class="customer-requests-view">
        <h1>My Service Requests</h1>

        <div class="card mb-4">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Status</label>
                        <select class="form-select" v-model="filters.status" @change="applyFilters">
                            <option value="">All Statuses</option>
                            <option value="requested">Requested</option>
                            <option value="assigned">Assigned</option>
                            <option value="completed">Completed</option>
                            <option value="closed">Closed</option>
                            <option value="cancelled">Cancelled</option>
                        </select>
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Date From</label>
                        <input type="date" class="form-control" v-model="filters.dateFrom" @change="applyFilters">
                    </div>
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Date To</label>
                        <input type="date" class="form-control" v-model="filters.dateTo" @change="applyFilters">
                    </div>
                </div>
                <div class="d-flex justify-content-end">
                    <button class="btn btn-secondary" @click="clearFilters">Clear Filters</button>
                </div>
            </div>
        </div>


        <div class="card">
            <div class="card-body">
                <div v-if="error">{{ error }}</div>
                <div v-if="loading" class="text-center my-5">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>

                <div v-else-if="filteredRequests.length === 0" class="text-center my-5">
                    <p>No service requests found matching the criteria.</p>
                    <button v-if="Object.values(filters).some(v => v !== '')" class="btn btn-primary"
                        @click="clearFilters">
                        Clear Filters
                    </button>
                    <router-link v-else to="/customer/services" class="btn btn-primary">
                        Browse Services
                    </router-link>
                </div>
                <div v-else>
                    <div class="list-group">

                        <div v-for="request in filteredRequests" :key="request.id" class="list-group-item">
                            <div class="d-flex justify-content-between">
                                <h5>{{ request.service_name }}</h5>
                                <small :class="getStatusBadgeClass(request.status)">{{ request.status }}</small>
                            </div>
                            <div>
                                <strong>Professional:</strong> {{ request.professional_name || 'Not assigned yet' }}
                                <small class="text-muted d-block">{{ formatDateTime(request.scheduled_date) }}</small>
                            </div>
                            <button class="btn btn-sm btn-outline-primary mt-2" @click="toggleDetails(request.id)">
                                {{ expandedRequestId === request.id ? 'Hide Details' : 'View Details' }}
                            </button>
                            <div v-if="expandedRequestId === request.id" class="mt-3">
                                <p><strong>Price:</strong> {{ formatPrice(request.base_price) }}</p>
                                <p><strong>Estimated Time:</strong> {{ formatDuration(request.estimated_time) }}</p>
                                <p v-if="request.remarks"><strong>Remarks:</strong> {{ request.remarks }}</p>

                                <div v-if="request.status === 'requested' && request.professional_id == null">
                                    <button class="btn btn-sm btn-outline-warning mt-2"
                                        v-if="request.status === 'requested'" @click="openEditModal(request)">
                                        Edit Request
                                    </button>
                                </div>

                                <div v-if="canCancelRequest(request)">
                                    <button class="btn btn-sm btn-danger" @click="cancelRequest(request.id)">Cancel
                                        Request</button>
                                </div>

                                <div v-if="request.professional_id !== null && request.status !== 'requested'">
                                    <!-- <button class="btn btn-sm btn-outline-info" @click="viewProfessional(request)">
                                        View Professional Details
                                    </button> -->
                                    <p><strong>Professional:</strong> {{ request.professional_name }}</p>
                                    <p><strong>Contact:</strong> {{ request.professional_phone }}</p>
                                    <p><strong>Rating:</strong> {{ (request.professional_rating === 0) ? 'You are the \
                                        first customer for this professional, Please leave a review and give him a \
                                        rating' : request.professional_rating }}</p>
                                </div>


                                <div v-if="request.status === 'completed'">
                                    <button class="btn btn-sm btn-success" @click="closeRequest(request.id)">Close
                                        Request</button>
                                </div>

                                <div v-if="showEditModal" class="modal-overlay">
                                    <div class="modal-content">
                                        <h2>Edit Request</h2>
                                        <form @submit.prevent="updateRequest">
                                            <div class="mb-3">
                                                <label class="form-label">Scheduled Date and Time:</label>
                                                <input type="datetime-local" class="form-control"
                                                    v-model="editData.scheduled_date" required>
                                            </div>

                                            <div class="mb-3">
                                                <label class="form-label">Remarks:</label>
                                                <textarea class="form-control" v-model="editData.remarks"></textarea>
                                            </div>

                                            <div class="d-flex justify-content-between">
                                                <button type="submit" class="btn btn-primary"
                                                    :disabled="requestStore.loading">
                                                    {{ requestStore.loading ? 'Saving...' : 'Save Changes' }}
                                                </button>
                                                <button type="button" class="btn btn-secondary"
                                                    @click="showEditModal = false">
                                                    Cancel
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>

                                <div v-if="canReviewRequest(request)">
                                    <h6 class="mt-3">Leave a Review</h6>
                                    <div class="rating-container mb-2">
                                        <label class="form-label">Rating (1-5):</label>
                                        <div class="numeric-rating">
                                            <div v-for="i in 5" :key="i"
                                                :class="['rating-number', { 'active': reviewForm.rating >= i }]"
                                                @click="reviewForm.rating = i">
                                                {{ i }}
                                            </div>
                                        </div>
                                        <small class="text-muted">Selected: {{ reviewForm.rating || 'None' }}/5</small>
                                    </div>
                                    <textarea v-model="reviewForm.comment" class="form-control mt-2"
                                        placeholder="Share your experience..."></textarea>
                                    <button class="btn btn-primary btn-sm mt-2" @click="submitReview1(request.id)"
                                        :disabled="reviewForm.rating === 0">
                                        Submit Review
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
import { ref, computed } from 'vue';
import { useRequestStore } from '@/stores/requests';
import { formatPrice, formatDuration, formatDateTime } from '@/utils/formatters';

const requestStore = useRequestStore();
const { fetchRequests, cancelRequest, updateExistingRequest, performRequestAction, setFilterOptions, submitReview } = requestStore;
const filters = ref({ status: '', dateFrom: '', dateTo: '' });
const expandedRequestId = ref(null);

const error = ref(null);
const showEditModal = ref(false);
const currentEditingRequest = ref(null);

const reviewForm = ref({ rating: 0, comment: '' });

const loading = computed(() => requestStore.loading);
const filteredRequests = computed(() => requestStore.filteredRequests);

const minDate = ref(new Date().toISOString().slice(0, 16));

const clearFilters = () => {
    filters.value = {
        status: '',
        dateFrom: '',
        dateTo: ''
    }
    requestStore.clearFilters()

    fetchRequests();
}


const getStatusBadgeClass = (status) => {
    if (status === 'closed') return 'badge bg-success';
    if (status === 'completed') return 'badge bg-primary';
    if (['in_progress', 'assigned'].includes(status)) return 'badge bg-info';
    if (status === 'requested') return 'badge bg-warning text-dark';
    if (status === 'cancelled') return 'badge bg-danger';
    return 'badge bg-secondary';
};

const canCancelRequest = (request) => ['requested'].includes(request.status);
const canReviewRequest = (request) => request.status === 'closed' && !request.has_review;
const toggleDetails = (id) => {
    if (expandedRequestId.value === id) {
        expandedRequestId.value = null;
    } else {
        expandedRequestId.value = id;
        showEditModal.value = false;
    }
};

const editData = ref({ scheduled_date: '', remarks: '' });

const openEditModal = (request) => {
    showEditModal.value = true;
    currentEditingRequest.value = request;
    editData.value.scheduled_date = request.scheduled_date;
    editData.value.remarks = request.remarks || '';
};



const updateRequest = async () => {
    if (!currentEditingRequest.value) return;

    try {
        const scheduledDate = new Date(editData.value.scheduled_date);
        const now = new Date();
        now.setMinutes(now.getMinutes() + 30); // Ensure at least 30 mins in the future

        if (scheduledDate < now) {
            alert('Please select a time at least 30 minutes in the future.');
            return;
        }

        // Convert to ISO format but keep local timezone offset
        scheduledDate.setMinutes(scheduledDate.getMinutes());
        await updateExistingRequest(currentEditingRequest.value.id, {
            scheduled_date: scheduledDate.toISOString(),
            remarks: editData.value.remarks
        });

        showEditModal.value = false;
        fetchRequests();
    } catch (err) {
        console.error('Failed to update request:', err);
    }
};


const applyFilters = () => {
    setFilterOptions(filters.value);
    fetchRequests();
};

const closeRequest = async (requestId) => {
    await performRequestAction(requestId, 'close');
    fetchRequests();
};

const submitReview1 = async (requestId) => {
    if (reviewForm.value.rating < 1) return;
    await submitReview({ service_request_id: requestId, rating: reviewForm.value.rating, comment: reviewForm.value.comment });
    fetchRequests();
    reviewForm.value = { rating: 0, comment: '' };
};

fetchRequests();
</script>

<style scoped>
.numeric-rating {
    display: flex;
    gap: 10px;
    margin-bottom: 5px;
}

.rating-number {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 1px solid #ccc;
    cursor: pointer;
    font-weight: bold;
    transition: all 0.2s ease;
}

.rating-number:hover {
    background-color: #e9ecef;
    border-color: #6c757d;
}

.rating-number.active {
    background-color: #007bff;
    color: white;
    border-color: #007bff;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    max-width: 500px;
    width: 100%;
}
</style>