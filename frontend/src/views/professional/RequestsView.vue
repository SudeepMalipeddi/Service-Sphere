<template>
    <div class="professional-requests-view">
        <h1>Service Requests</h1>

        <ul class="nav nav-tabs mb-4">
            <li class="nav-item">
                <a class="nav-link" :class="{ active: activeTab === 'my' }" @click.prevent="activeTab = 'my'" href="#">
                    My Requests
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" :class="{ active: activeTab === 'available' }"
                    @click.prevent="activeTab = 'available'" href="#">
                    Available Requests
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" :class="{ active: activeTab === 'rejected' }"
                    @click.prevent="activeTab = 'rejected'" href="#">
                    Rejected Requests
                </a>
            </li>
        </ul>


        <div v-if="activeTab === 'my'">

            <div class="card mb-4">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Status</label>
                            <select class="form-select" v-model="myFilters.status" @change="applyMyFilters">
                                <option value="">All Statuses</option>
                                <option value="assigned">Assigned</option>
                                <option value="completed">Completed</option>
                                <option value="closed">Closed</option>
                            </select>
                        </div>

                        <div class="col-md-4 mb-3">
                            <label class="form-label">Date From</label>
                            <input type="date" class="form-control" v-model="myFilters.dateFrom"
                                @change="applyMyFilters">
                        </div>

                        <div class="col-md-4 mb-3">
                            <label class="form-label">Date To</label>
                            <input type="date" class="form-control" v-model="myFilters.dateTo" @change="applyMyFilters">
                        </div>
                    </div>

                    <div class="d-flex justify-content-end">
                        <button class="btn btn-secondary" @click="clearMyFilters">Clear Filters</button>
                    </div>
                </div>
            </div>


            <div class="card">
                <div class="card-body">
                    <div v-if="loading" class="text-center my-5">
                        <div class="spinner-border" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>

                    <div v-else-if="filteredRequests.length === 0" class="text-center my-5">
                        <p>No service requests found matching the criteria.</p>
                        <button v-if="Object.values(myFilters).some(v => v !== '')" class="btn btn-primary"
                            @click="clearMyFilters">
                            Clear Filters
                        </button>
                        <button v-else class="btn btn-primary" @click="activeTab = 'available'">
                            Browse Available Requests
                        </button>
                    </div>

                    <div v-else class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Service</th>
                                    <th>Customer</th>
                                    <th>Scheduled Date</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="request in filteredRequests" :key="request.id">
                                    <td>{{ request.id }}</td>
                                    <td>{{ request.service_name }}</td>
                                    <td>{{ request.customer_name }}</td>
                                    <td>{{ formatDate(request.scheduled_date) }}</td>
                                    <td>
                                        <span :class="getStatusBadgeClass(request.status)">
                                            {{ request.status }}
                                        </span>
                                    </td>
                                    <td>
                                        <div class="btn-group">
                                            <button class="btn btn-sm btn-outline-primary"
                                                @click="selectedRequest = request; isRequestDetailsOpen = true">
                                                View Details
                                            </button>

                                            <button v-if="request.status === 'assigned'" class="btn btn-sm btn-success"
                                                @click="completeRequest(request.id)">
                                                Complete
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>


        <div v-else-if="activeTab === 'available'">
            <div class="card">
                <div class="card-body">
                    <div v-if="availableLoading" class="text-center my-5">
                        <div class="spinner-border" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>

                    <div v-else-if="!isVerified" class="alert alert-warning">
                        <h5>Account Verification Required</h5>
                        <p>Your account needs to be verified before you can accept service requests.</p>
                        <router-link to="/professional/profile" class="btn btn-primary">
                            Go to Profile
                        </router-link>
                    </div>

                    <div v-else-if="availableRequests.length === 0" class="text-center my-5">
                        <p>There are no available service requests at the moment.</p>
                        <p>Please check back later for new requests.</p>
                    </div>

                    <div v-else>

                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="includeRejectedSwitch"
                                v-model="includeRejected" @change="fetchAvailableRequests">
                            <label class="form-check-label" for="includeRejectedSwitch">Include requests I've previously
                                rejected</label>
                        </div>

                        <div class="row">
                            <div class="col-md-6 mb-4" v-for="request in availableRequests" :key="request.id">
                                <div class="card h-100" :class="{ 'border-danger': isRequestRejected(request.id) }">
                                    <div class="card-header d-flex justify-content-between align-items-center">
                                        <h5 class="mb-0">{{ request.service_name }}</h5>
                                        <span v-if="isRequestRejected(request.id)" class="badge bg-danger">
                                            Previously Rejected
                                        </span>
                                    </div>
                                    <div class="card-body">
                                        <p><strong>Customer:</strong> {{ request.customer_name }}</p>
                                        <p><strong>Scheduled Date:</strong> {{ formatDateTime(request.scheduled_date) }}
                                        </p>
                                        <p><strong>Location:</strong> {{ request.customer_address || 'Not specified' }}
                                        </p>
                                        <p v-if="request.remarks"><strong>Notes:</strong> {{ request.remarks }}</p>

                                        <div class="d-flex justify-content-between align-items-center mt-3">
                                            <span class="fw-bold">{{ formatPrice(request.base_price) }}</span>
                                            <div class="btn-group">
                                                <button class="btn btn-success" @click="acceptRequest(request.id)"
                                                    :disabled="availableActionLoading || isRequestRejected(request.id)">
                                                    <span
                                                        v-if="availableActionLoading && actionRequestId === request.id"
                                                        class="spinner-border spinner-border-sm" role="status"
                                                        aria-hidden="true"></span>
                                                    Accept
                                                </button>
                                                <button class="btn btn-outline-danger" @click="openRejectModal(request)"
                                                    :disabled="availableActionLoading || isRequestRejected(request.id)">
                                                    Reject
                                                </button>
                                                <button v-if="isRequestRejected(request.id)"
                                                    class="btn btn-outline-secondary"
                                                    @click="viewRejectionDetails(request.id)">
                                                    View Rejection
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>


        <div v-else-if="activeTab === 'rejected'">
            <div class="card">
                <div class="card-body">
                    <div v-if="rejectedLoading" class="text-center my-5">
                        <div class="spinner-border" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>

                    <div v-else-if="rejectedRequests.length === 0" class="text-center my-5">
                        <p>You have not rejected any service requests.</p>
                    </div>

                    <div v-else>
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Request ID</th>
                                        <th>Service</th>
                                        <th>Customer</th>
                                        <th>Rejection Date</th>
                                        <th>Reason</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="rejection in rejectedRequests" :key="rejection.id">
                                        <td>{{ rejection.service_request_id }}</td>
                                        <td>{{ rejection.service_name || 'N/A' }}</td>
                                        <td>{{ rejection.customer_name || 'N/A' }}</td>
                                        <td>{{ formatDateTime(rejection.rejected_at) }}</td>
                                        <td>{{ rejection.reason || 'No reason provided' }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>


        <div v-if="isRequestDetailsOpen && selectedRequest"
            class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
            style="background-color: rgba(255,255,255,0.95); z-index: 1050;">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Service Request Details</h5>
                        <button type="button" class="btn-close" @click="isRequestDetailsOpen = false"
                            aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Service Information</h6>
                                <p><strong>Service:</strong> {{ selectedRequest.service_name }}</p>
                                <p><strong>Price:</strong> {{ formatPrice(selectedRequest.base_price) }}</p>
                                <p><strong>Estimated Time:</strong> {{ formatDuration(selectedRequest.estimated_time) }}
                                </p>
                            </div>

                            <div class="col-md-6">
                                <h6>Request Information</h6>
                                <p><strong>Status:</strong>
                                    <span :class="getStatusBadgeClass(selectedRequest.status)">
                                        {{ selectedRequest.status }}
                                    </span>
                                </p>
                                <p><strong>Scheduled Date:</strong> {{ formatDateTime(selectedRequest.scheduled_date) }}
                                </p>
                                <p v-if="selectedRequest.completion_date">
                                    <strong>Completion Date:</strong> {{ formatDateTime(selectedRequest.completion_date)
                                    }}
                                </p>
                            </div>
                        </div>

                        <div class="row mt-3">
                            <div class="col-md-6">
                                <h6>Customer Information</h6>
                                <p><strong>Name:</strong> {{ selectedRequest.customer_name }}</p>
                                <p v-if="selectedRequest.customer_phone">
                                    <strong>Phone:</strong> {{ selectedRequest.customer_phone }}
                                </p>
                                <p v-if="selectedRequest.customer_address">
                                    <strong>Customer Address:</strong> {{ selectedRequest.customer_address }}
                                </p>
                            </div>

                            <div class="col-md-6">
                                <h6>Additional Information</h6>
                                <p>{{ selectedRequest.remarks || 'No additional information provided' }}</p>
                            </div>
                        </div>

                        <div class="row mt-3" v-if="selectedRequest.status === 'closed' && selectedRequest.review">
                            <div class="col-12">
                                <h6>Customer Review</h6>
                                <div class="card">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-center mb-2">
                                            <div class="star-rating">
                                                <span v-for="i in 5" :key="i"
                                                    :class="{ 'filled': selectedRequest.review.rating >= i }">
                                                    ★
                                                </span>
                                            </div>
                                            <small class="text-muted">{{ formatDate(selectedRequest.review.created_at)
                                                }}</small>
                                        </div>
                                        <p>{{ selectedRequest.review.comment || 'No comment provided' }}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary"
                            @click="isRequestDetailsOpen = false">Close</button>

                        <button v-if="selectedRequest.status === 'assigned'" class="btn btn-success"
                            @click="completeRequest(selectedRequest.id); isRequestDetailsOpen = false">
                            Complete
                        </button>
                    </div>
                </div>
            </div>
        </div>


        <div v-if="isRejectModalOpen && selectedRequest"
            class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
            style="background-color: rgba(255,255,255,0.95); z-index: 1050;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Rejection Reason</h5>
                        <button type="button" class="btn-close" @click="isRejectModalOpen = false"
                            aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>Please provide a reason for rejecting this service request:</p>

                        <div class="mb-3">
                            <label for="rejectReason" class="form-label">Reason</label>
                            <textarea class="form-control" id="rejectReason" v-model="rejectReason" rows="3"
                                placeholder="E.g., schedule conflict, location too far, etc."></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary"
                            @click="isRejectModalOpen = false">Cancel</button>
                        <button type="button" class="btn btn-danger" @click="rejectRequest"
                            :disabled="availableActionLoading">
                            <span v-if="availableActionLoading" class="spinner-border spinner-border-sm" role="status"
                                aria-hidden="true"></span>
                            Reject Request
                        </button>
                    </div>
                </div>
            </div>
        </div>


        <div v-if="isRejectionDetailsOpen && selectedRejection"
            class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
            style="background-color: rgba(255,255,255,0.95); z-index: 1050;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Rejection Details</h5>
                        <button type="button" class="btn-close" @click="isRejectionDetailsOpen = false"
                            aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p><strong>Request ID:</strong> {{ selectedRejection.service_request_id }}</p>
                        <p><strong>Rejected By:</strong> {{ selectedRejection.professional_name }}</p>
                        <p><strong>Rejected On:</strong> {{ formatDateTime(selectedRejection.rejected_at) }}</p>
                        <p><strong>Reason:</strong></p>
                        <div class="card">
                            <div class="card-body">
                                {{ selectedRejection.reason || 'No reason provided' }}
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary"
                            @click="isRejectionDetailsOpen = false">Close</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useRequestStore } from '@/stores/requests'
import { formatDate, formatDateTime, formatPrice, formatDuration } from '@/utils/formatters'
import axios from 'axios'


const route = useRoute()
const activeTab = ref(route.query.available === 'true' ? 'available' : 'my')
const myFilters = reactive({
    status: route.query.status || '',
    dateFrom: route.query.date_from || '',
    dateTo: route.query.date_to || '',
})
const availableRequests = ref([])
const availableLoading = ref(false)
const availableActionLoading = ref(false)
const actionRequestId = ref(null)
const selectedRequest = ref(null)
const rejectReason = ref('')
const isVerified = ref(false)
const includeRejected = ref(false)


const rejectedRequests = ref([])
const rejectedLoading = ref(false)
const rejectedRequestIds = ref([])
const selectedRejection = ref(null)


const isRequestDetailsOpen = ref(false)
const isRejectModalOpen = ref(false)
const isRejectionDetailsOpen = ref(false)


const requestStore = useRequestStore()
const { requests, filteredRequests, loading } = storeToRefs(requestStore)
const { fetchRequests, performRequestAction, setFilterOptions, clearFilters } = requestStore


const getStatusBadgeClass = (status) => {
    if (status === 'closed') return 'badge bg-success'
    if (status === 'completed') return 'badge bg-primary'
    if (status === 'assigned') return 'badge bg-warning text-dark'
    if (status === 'requested') return 'badge bg-secondary'
    if (status === 'cancelled') return 'badge bg-danger'
    return 'badge bg-secondary'
}

const applyMyFilters = () => {
    setFilterOptions(myFilters)
    fetchRequests()
}

const clearMyFilters = () => {
    myFilters.status = ''
    myFilters.dateFrom = ''
    myFilters.dateTo = ''
    clearFilters()
    fetchRequests()
}

const fetchAvailableRequests = async () => {
    availableLoading.value = true

    try {
        const response = await axios.get('/service-requests', {
            params: {
                available: true,
                include_rejected: includeRejected.value
            },
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        })

        availableRequests.value = response.data.service_requests

    } catch (error) {
        console.error('Fetch available requests error:', error)
        const event = new CustomEvent('show-error', { detail: 'Failed to load available requests' })
        window.dispatchEvent(event)
    } finally {
        availableLoading.value = false
    }
}

const fetchRejectedRequests = async () => {
    rejectedLoading.value = true

    try {
        const response = await axios.get('/rejected-requests', {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        })

        rejectedRequests.value = response.data.rejections


        rejectedRequestIds.value = rejectedRequests.value
            .filter(rejection => rejection.is_own_rejection)
            .map(rejection => rejection.service_request_id)

    } catch (error) {
        console.error('Fetch rejected requests error:', error)
        const event = new CustomEvent('show-error', { detail: 'Failed to load rejected requests' })
        window.dispatchEvent(event)
    } finally {
        rejectedLoading.value = false
    }
}

const isRequestRejected = (requestId) => {
    return rejectedRequestIds.value.includes(requestId)
}

const viewRejectionDetails = async (requestId) => {
    try {
        const response = await axios.get(`/rejected-requests/${requestId}`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        })

        const rejections = response.data.rejections

        const ownRejection = rejections.find(rejection => rejection.is_own_rejection)

        if (ownRejection) {
            selectedRejection.value = ownRejection
            isRejectionDetailsOpen.value = true
        } else {
            const event = new CustomEvent('show-error', { detail: 'Rejection details not found' })
            window.dispatchEvent(event)
        }
    } catch (error) {
        console.error('Fetch rejection details error:', error)
        const event = new CustomEvent('show-error', { detail: 'Failed to load rejection details' })
        window.dispatchEvent(event)
    }
}

const fetchProfessionalStatus = async () => {
    try {
        const user = JSON.parse(localStorage.getItem('user'))
        console.log('User ID:', user.professional_id)

        const response = await axios.get(`/professionals/${user.professional_id}`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        })
        isVerified.value = response.data.professional.verification_status === 'approved'
    } catch (error) {
        console.error('Fetch professional status error:', error)
    }
}

const completeRequest = async (requestId) => {
    try {
        await performRequestAction(requestId, 'complete')


        isRequestDetailsOpen.value = false


        const event = new CustomEvent('show-success', { detail: 'Service request marked as completed' })
        window.dispatchEvent(event)


        fetchRequests()
    } catch (error) {
        console.error('Complete request error:', error)
        const event = new CustomEvent('show-error', { detail: 'Failed to complete service request' })
        window.dispatchEvent(event)
    }
}

const acceptRequest = async (requestId) => {
    availableActionLoading.value = true
    actionRequestId.value = requestId

    try {
        await axios.post(`/service-requests/${requestId}/action`, {
            action: 'accept'
        }, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        })


        const event = new CustomEvent('show-success', { detail: 'Service request accepted successfully' })
        window.dispatchEvent(event)


        fetchAvailableRequests()


        fetchRequests()
    } catch (error) {
        console.error('Accept request error:', error)
        const event = new CustomEvent('show-error', {
            detail: error.response?.data?.message || 'Failed to accept service request'
        })
        window.dispatchEvent(event)
    } finally {
        availableActionLoading.value = false
        actionRequestId.value = null
    }
}

const openRejectModal = (request) => {
    selectedRequest.value = request
    rejectReason.value = ''
    isRejectModalOpen.value = true
}

const rejectRequest = async () => {
    if (!selectedRequest.value) return

    availableActionLoading.value = true
    actionRequestId.value = selectedRequest.value.id

    try {
        await axios.post(`/service-requests/${selectedRequest.value.id}/action`, {
            action: 'reject',
            reason: rejectReason.value
        }, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        })


        isRejectModalOpen.value = false


        const event = new CustomEvent('show-success', { detail: 'Service request rejected successfully' })
        window.dispatchEvent(event)


        fetchAvailableRequests()


        fetchRejectedRequests()
    } catch (error) {
        console.error('Reject request error:', error)
        const event = new CustomEvent('show-error', { detail: 'Failed to reject service request' })
        window.dispatchEvent(event)
    } finally {
        availableActionLoading.value = false
        actionRequestId.value = null
    }
}

const init = async () => {

    await fetchRejectedRequests()


    if (activeTab.value === 'available') {
        await fetchProfessionalStatus()
        fetchAvailableRequests()
    } else if (activeTab.value === 'rejected') {

    } else {
        if (myFilters.status || myFilters.dateFrom || myFilters.dateTo) {
            setFilterOptions(myFilters)
        }
        await fetchRequests()
    }
}


watch(activeTab, (newVal) => {
    if (newVal === 'available') {
        fetchProfessionalStatus()
        fetchAvailableRequests()
    } else if (newVal === 'rejected') {
        fetchRejectedRequests()
    } else {
        fetchRequests()
    }
})
init()
</script>

<style scoped>
.star-rating {
    display: inline-block;
}

.star-rating span {
    font-size: 18px;
    color: #ccc;
    padding: 0 2px;
}

.star-rating span.filled {
    color: #ffc107;
}
</style>