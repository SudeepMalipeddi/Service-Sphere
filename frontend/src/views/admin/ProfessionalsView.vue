<template>
    <div class="admin-professionals-view">
        <h1>Manage Professionals</h1>

        <!-- Filters -->
        <div class="card mb-4">
            <div class="card-body">
                <h5 class="card-title">Filters</h5>
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Status</label>
                        <select class="form-select" v-model="filters.status" @change="applyFilters">
                            <option value="">All Statuses</option>
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>
                    </div>

                    <div class="col-md-4 mb-3">
                        <label class="form-label">Service</label>
                        <select class="form-select" v-model="filters.service_id" @change="applyFilters">
                            <option value="">All Services</option>
                            <option v-for="service in services" :key="service.id" :value="service.id">
                                {{ service.name }}
                            </option>
                        </select>
                    </div>

                    <div class="col-md-4 mb-3">
                        <label class="form-label">Verification Status</label>
                        <select class="form-select" v-model="filters.verification_status" @change="applyFilters">
                            <option value="">All Statuses</option>
                            <option value="pending">Pending</option>
                            <option value="approved">Approved</option>
                            <option value="rejected">Rejected</option>
                        </select>
                    </div>
                </div>

                <div class="d-flex justify-content-end">
                    <button class="btn btn-secondary" @click="clearFilters">Clear Filters</button>
                </div>
            </div>
        </div>

        <!-- Professionals list -->
        <div class="card">
            <div class="card-body">
                <div v-if="loading" class="text-center my-5">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>

                <div v-else-if="filteredProfessionals.length === 0" class="text-center my-5">
                    <p>No professionals found matching the criteria.</p>
                </div>

                <div v-else class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Service</th>
                                <th>Experience</th>
                                <th>Verification</th>
                                <th>Status</th>
                                <th>Rating</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="professional in filteredProfessionals" :key="professional.id">
                                <td>{{ professional.id }}</td>
                                <td>
                                    {{ professional.name }}
                                    <div><small class="text-muted">{{ professional.email }}</small></div>
                                </td>
                                <td>{{ professional.service_name }}</td>
                                <td>{{ professional.years_experience }} years</td>
                                <td>
                                    <span :class="getVerificationBadgeClass(professional.verification_status)">
                                        {{ professional.verification_status }}
                                    </span>
                                </td>
                                <td>
                                    <span :class="getStatusBadgeClass(professional.user?.is_active)">
                                        {{ professional.user?.is_active ? 'Active' : 'Inactive' }}
                                    </span>
                                </td>
                                <td>
                                    <div class="d-flex align-items-center">
                                        <span>{{ professional.rating }}</span>
                                        <i class="bi bi-star-fill text-warning ms-1"></i>
                                    </div>
                                </td>
                                <td>
                                    <div class="btn-group">
                                        <button class="btn btn-sm"
                                            :class="professional.user?.is_active ? 'btn-danger' : 'btn-success'"
                                            @click="toggleStatus(professional)">
                                            {{ professional.user?.is_active ? 'Block' : 'Unblock' }}
                                        </button>

                                        <button
                                            v-if="professional.verification_status === 'pending' && professional.documents_url.length > 0"
                                            class="btn btn-sm btn-primary" @click="showVerificationForm(professional)">
                                            Verify
                                        </button>

                                        <button class="btn btn-sm btn-info"
                                            @click="showProfessionalDetails(professional)">
                                            View
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Verification Form (No Modal) -->
        <div v-if="isVerificationFormVisible" class="card mt-4">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="m-0">Verify Professional</h5>
                <button type="button" class="btn-close" @click="hideVerificationForm"></button>
            </div>
            <div class="card-body" v-if="selectedProfessional">
                <div class="mb-3">
                    <h6>{{ selectedProfessional.name }}</h6>
                    <p class="text-muted">Service: {{ selectedProfessional.service_name }}</p>
                    <p>{{ selectedProfessional.bio }}</p>

                    <div v-if="selectedProfessional.documents_url && selectedProfessional.documents_url.length > 0">
                        <h6>Documents:</h6>
                        <div class="list-group">
                            <a v-for="(doc, index) in selectedProfessional.documents_url" :key="index" :href="doc"
                                target="_blank" class="list-group-item list-group-item-action">
                                Document {{ index + 1 }}
                            </a>
                        </div>
                    </div>
                </div>

                <div class="mb-3">
                    <label class="form-label">Verification Action</label>
                    <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check" name="action" id="action-approve" value="approve"
                            v-model="verificationAction">
                        <label class="btn btn-outline-success" for="action-approve">Approve</label>

                        <input type="radio" class="btn-check" name="action" id="action-reject" value="reject"
                            v-model="verificationAction">
                        <label class="btn btn-outline-danger" for="action-reject">Reject</label>
                    </div>
                </div>

                <div class="mb-3">
                    <label for="verificationMessage" class="form-label">Message</label>
                    <textarea class="form-control" id="verificationMessage" v-model="verificationMessage" rows="3"
                        :placeholder="`Reason for ${verificationAction === 'approve' ? 'approval' : 'rejection'}`"></textarea>
                </div>
            </div>
            <div class="card-footer d-flex justify-content-end">
                <button type="button" class="btn btn-secondary me-2" @click="hideVerificationForm">Cancel</button>
                <button type="button" class="btn"
                    :class="verificationAction === 'approve' ? 'btn-success' : 'btn-danger'" @click="submitVerification"
                    :disabled="!verificationAction">
                    {{ verificationAction === 'approve' ? 'Approve' : 'Reject' }}
                </button>
            </div>
        </div>

        <!-- Professional Details (No Modal) -->
        <div v-if="isDetailsVisible" class="card mt-4">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="m-0">Professional Details</h5>
                <button type="button" class="btn-close" @click="hideDetails"></button>
            </div>
            <div class="card-body" v-if="selectedProfessional">
                <div class="row">
                    <div class="col-md-6">
                        <h6>Personal Information</h6>
                        <p><strong>Name:</strong> {{ selectedProfessional.name }}</p>
                        <p><strong>Email:</strong> {{ selectedProfessional.email }}</p>
                        <p><strong>Phone:</strong> {{ selectedProfessional.phone || 'Not provided' }}</p>
                        <p><strong>Joined:</strong> {{ formatDate(selectedProfessional.registered_on) }}</p>
                    </div>

                    <div class="col-md-6">
                        <h6>Professional Information</h6>
                        <p><strong>Service:</strong> {{ selectedProfessional.service_name }}</p>
                        <p><strong>Experience:</strong> {{ selectedProfessional.years_experience }} years</p>
                        <p><strong>Verification:</strong> {{ selectedProfessional.verification_status }}</p>
                        <p><strong>Rating:</strong> {{ selectedProfessional.rating }} / 5</p>
                    </div>
                </div>

                <div class="mt-3">
                    <h6>Bio</h6>
                    <p>{{ selectedProfessional.bio || 'No bio provided' }}</p>
                </div>

                <div v-if="selectedProfessional.documents_url && selectedProfessional.documents_url.length > 0"
                    class="mt-3">
                    <h6>Documents</h6>
                    <div class="list-group">
                        <a v-for="(doc, index) in selectedProfessional.documents_url" :key="index" :href="doc"
                            target="_blank" class="list-group-item list-group-item-action">
                            Document {{ index + 1 }}
                        </a>
                    </div>
                </div>
                <div v-else class="alert alert-warning mt-3 mb-0">
                    <p>No documents uploaded by professional yet.</p>
                    <p>Please wait till professional uploads</p>
                </div>
            </div>
            <div class="card-footer d-flex justify-content-end">
                <button type="button" class="btn btn-secondary" @click="hideDetails">Close</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useServiceStore } from '@/stores/services'
import { formatDate } from '@/utils/formatters'

// Initialize stores
const adminStore = useAdminStore()
const serviceStore = useServiceStore()
const route = useRoute()

// Reactive state
const filters = reactive({
    status: '',
    service_id: '',
    verification_status: ''
})

const selectedProfessional = ref(null)
const verificationAction = ref('approve')
const verificationMessage = ref('')
const isVerificationFormVisible = ref(false)
const isDetailsVisible = ref(false)

// Computed properties 
const loading = computed(() => adminStore.loading)
const filteredProfessionals = computed(() => adminStore.filteredProfessionals)
const services = computed(() => serviceStore.services)

// Methods
const getVerificationBadgeClass = (status) => {
    if (status === 'approved') return 'badge bg-success'
    if (status === 'rejected') return 'badge bg-danger'
    return 'badge bg-warning text-dark'
}

const getStatusBadgeClass = (isActive) => {
    return isActive ? 'badge bg-success' : 'badge bg-danger'
}

const toggleStatus = async (professional) => {
    try {
        const newStatus = professional.user?.is_active ? 'inactive' : 'active'
        console.log(professional.is_active)
        await adminStore.updateProfessionalActiveStatus(professional.id, newStatus)
        window.dispatchEvent(new CustomEvent('show-success', {
            detail: `Professional ${newStatus === 'active' ? 'activated' : 'deactivated'} successfully`
        }))
    } catch (error) {
        console.error('Toggle status error:', error)
        window.dispatchEvent(new CustomEvent('show-error', {
            detail: 'Failed to update professional status'
        }))
    }
}
const showVerificationForm = (professional) => {
    selectedProfessional.value = professional
    verificationAction.value = 'approve'
    verificationMessage.value = ''
    isVerificationFormVisible.value = true
    isDetailsVisible.value = false
}

const hideVerificationForm = () => {
    isVerificationFormVisible.value = false
}

const showProfessionalDetails = (professional) => {
    selectedProfessional.value = professional
    isDetailsVisible.value = true
    isVerificationFormVisible.value = false
}

const hideDetails = () => {
    isDetailsVisible.value = false
}

const submitVerification = async () => {
    if (!selectedProfessional.value || !verificationAction.value) return

    try {
        await adminStore.verifyProfessionalStatus(
            selectedProfessional.value.id,
            verificationAction.value,
            verificationMessage.value
        )
        isVerificationFormVisible.value = false
        window.dispatchEvent(new CustomEvent('show-success', {
            detail: `Professional ${verificationAction.value === 'approve' ? 'approved' : 'rejected'} successfully`
        }))
    } catch (error) {
        console.error('Verification error:', error)
        window.dispatchEvent(new CustomEvent('show-error', {
            detail: 'Failed to verify professional'
        }))
    }
}

const applyFilters = () => {
    adminStore.setProfessionalFilters(filters)
    adminStore.fetchProfessionals()
}

const clearFilters = () => {
    filters.status = ''
    filters.service_id = ''
    filters.verification_status = ''
    adminStore.clearProfessionalFilters()
    adminStore.fetchProfessionals()
}

onMounted(async () => {

    const { status, service_id, verification_status } = route.query
    if (status || service_id || verification_status) {
        filters.status = status || ''
        filters.service_id = service_id || ''
        filters.verification_status = verification_status || ''
        adminStore.setProfessionalFilters(filters)
    }

    await Promise.all([
        adminStore.fetchProfessionals(),
        serviceStore.fetchServices({ show_inactive: true })
    ])
})
</script>