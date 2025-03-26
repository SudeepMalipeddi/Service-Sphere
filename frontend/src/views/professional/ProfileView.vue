<template>
    <div class="container mt-4">
        <h1 class="mb-4">Professional Profile</h1>

        <!-- Loading State -->
        <div v-if="loading" class="text-center my-5">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">Loading profile data...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger">
            {{ error }}
        </div>

        <!-- Profile Content -->
        <div v-if="profile" class="row">
            <!-- Profile Information Card -->
            <div class="col-lg-8 mb-4">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Profile Information</h5>
                        <button v-if="!editMode" class="btn btn-primary btn-sm" @click="editMode = true">
                            <i class="bi bi-pencil"></i> Edit Profile
                        </button>
                    </div>

                    <div class="card-body">
                        <!-- Status Alerts -->
                        <div v-if="profile.verification_status === 'pending'" class="alert alert-warning mb-3">
                            <strong>Pending Verification:</strong> Our team is reviewing your information.
                            <span v-if="!hasDocuments">Please upload verification documents.</span>
                        </div>

                        <div v-if="profile.verification_status === 'rejected'" class="alert alert-danger mb-3">
                            <strong>Verification Rejected:</strong> {{ profile.verification_reason || 'No reason \
                            provided' }}
                        </div>

                        <div v-if="profile.verification_status === 'approved'" class="alert alert-success mb-3">
                            <strong>Verified:</strong> Your profile is approved.
                        </div>

                        <!-- View Mode -->
                        <div v-if="!editMode">
                            <div class="row mb-3 align-items-center">
                                <div class="col-md-3 text-center mb-3 mb-md-0">
                                    <div class="avatar-circle bg-primary text-white">
                                        {{ getInitials(profile.name) }}
                                    </div>
                                </div>
                                <div class="col-md-9">
                                    <h4>{{ profile.name }}</h4>
                                    <p class="mb-1">{{ profile.service_name }}</p>
                                    <span class="badge" :class="getStatusBadgeClass(profile.verification_status)">
                                        {{ profile.verification_status }}
                                    </span>
                                </div>
                            </div>

                            <hr>

                            <div class="row mb-2">
                                <div class="col-md-3 fw-bold">Email:</div>
                                <div class="col-md-9">{{ profile.email }}</div>
                            </div>

                            <div class="row mb-2">
                                <div class="col-md-3 fw-bold">Phone:</div>
                                <div class="col-md-9">{{ profile.phone }}</div>
                            </div>

                            <div class="row mb-2">
                                <div class="col-md-3 fw-bold">Experience:</div>
                                <div class="col-md-9">{{ profile.years_experience }} years</div>
                            </div>

                            <div class="row mb-2" v-if="profile.bio">
                                <div class="col-md-3 fw-bold">Bio:</div>
                                <div class="col-md-9">{{ profile.bio }}</div>
                            </div>
                        </div>

                        <!-- Edit Mode -->
                        <form v-else @submit.prevent="updateProfile">
                            <div class="mb-3">
                                <label for="name" class="form-label">Full Name</label>
                                <input type="text" class="form-control" id="name" v-model="editData.name" required>
                            </div>

                            <div class="mb-3">
                                <label for="phone" class="form-label">Phone Number</label>
                                <input type="tel" class="form-control" id="phone" v-model="editData.phone" required>
                            </div>

                            <div class="mb-3">
                                <label for="experience" class="form-label">Years of Experience</label>
                                <input type="number" class="form-control" id="experience"
                                    v-model="editData.years_experience" min="0" required>
                            </div>

                            <div class="mb-3">
                                <label for="bio" class="form-label">Professional Bio</label>
                                <textarea class="form-control" id="bio" v-model="editData.bio" rows="4"></textarea>
                            </div>

                            <div class="d-flex justify-content-end">
                                <button type="button" class="btn btn-secondary me-2" @click="cancelEdit">Cancel</button>
                                <button type="submit" class="btn btn-primary" :disabled="updating">
                                    <span v-if="updating" class="spinner-border spinner-border-sm me-1"></span>
                                    {{ updating ? 'Saving...' : 'Save Changes' }}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Documents Card -->
            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Verification Documents</h5>
                    </div>

                    <div class="card-body">
                        <!-- Has Documents -->
                        <div v-if="hasDocuments">
                            <p>Uploaded Documents:</p>
                            <ul class="list-group mb-3">
                                <li v-for="(doc, index) in profile.documents_url" :key="index"
                                    class="list-group-item d-flex justify-content-between align-items-center">
                                    <span>Document {{ index + 1 }}</span>
                                    <a :href="doc" target="_blank" class="btn btn-sm btn-outline-primary">
                                        <i class="bi bi-eye"></i> View
                                    </a>
                                </li>
                            </ul>

                            <button v-if="showUploadForm" class="btn btn-secondary btn-sm"
                                @click="showUploadForm = false">
                                Cancel Upload
                            </button>
                            <button v-else class="btn btn-primary btn-sm" @click="showUploadForm = true">
                                Upload Additional Document
                            </button>
                        </div>

                        <!-- No Documents -->
                        <div v-else>
                            <p class="text-center mb-3">
                                <i class="bi bi-file-earmark-x fs-1"></i>
                            </p>
                            <p>No documents uploaded yet. Please upload verification documents like:</p>
                            <ul>
                                <li>Government-issued ID</li>
                                <li>Professional certification</li>
                                <li>Experience certificates</li>
                            </ul>

                            <button class="btn btn-primary w-100" @click="showUploadForm = true">
                                Upload Document
                            </button>
                        </div>

                        <!-- Upload Form -->
                        <div v-if="showUploadForm" class="mt-3">
                            <div class="mb-3">
                                <label for="document" class="form-label">Select Document</label>
                                <input type="file" class="form-control" id="document" @change="handleFileSelect"
                                    accept=".pdf,.jpg,.jpeg,.png">
                                <div class="form-text">Max size: 5MB. Formats: PDF, JPG, PNG</div>
                            </div>

                            <button class="btn btn-primary" @click="uploadDocument" :disabled="uploading">
                                <span v-if="uploading" class="spinner-border spinner-border-sm me-1"></span>
                                {{ uploading ? 'Uploading...' : 'Upload' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getProfessional, updateProfessionalProfile, uploadDocuments } from '@/api/professional';
import { getUser } from '@/utils/authutils';
import { isValidPhone } from '@/utils/validators';

// State
const profile = ref(null);
const loading = ref(true);
const error = ref(null);
const editMode = ref(false);
const updating = ref(false);
const uploading = ref(false);
const selectedFile = ref(null);
const showUploadForm = ref(false);

// Edit form data
const editData = ref({
    name: '',
    phone: '',
    years_experience: 0,
    bio: ''
});

// Computed properties
const hasDocuments = computed(() => {
    return profile.value &&
        profile.value.documents_url &&
        profile.value.documents_url.length > 0;
});

// Helper functions
const getInitials = (name) => {
    if (!name) return '';
    return name.split(' ')
        .map(word => word.charAt(0).toUpperCase())
        .join('')
        .substring(0, 2);
};

const getStatusBadgeClass = (status) => {
    switch (status) {
        case 'approved': return 'bg-success';
        case 'pending': return 'bg-warning text-dark';
        case 'rejected': return 'bg-danger';
        default: return 'bg-secondary';
    }
};

// Lifecycle hooks
onMounted(async () => {
    await fetchProfile();
});

// Methods
const fetchProfile = async () => {
    loading.value = true;
    error.value = null;

    try {
        const user = getUser();
        if (user?.id && user.role === 'professional') {
            const professionalId = user.professional_id;
            if (professionalId) {
                const response = await getProfessional(professionalId);
                profile.value = response.data.professional;

                // Initialize edit data
                editData.value = {
                    name: profile.value.name,
                    phone: profile.value.phone,
                    years_experience: profile.value.years_experience,
                    bio: profile.value.bio || ''
                };
            }
        }
    } catch (err) {
        console.error('Failed to fetch profile:', err);
        error.value = 'Failed to load profile data. Please try again.';
    } finally {
        loading.value = false;
    }
};

const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
        selectedFile.value = file;
    }
};

const uploadDocument = async () => {
    if (!selectedFile.value) {
        alert('Please select a file to upload');
        return;
    }

    // Check file size (max 5MB)
    if (selectedFile.value.size > 5 * 1024 * 1024) {
        alert('File size exceeds 5MB limit');
        return;
    }

    // Check file type
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(selectedFile.value.type)) {
        alert('Only PDF, JPEG, and PNG files are allowed');
        return;
    }

    uploading.value = true;

    try {
        const formData = new FormData();
        formData.append('document', selectedFile.value);

        await uploadDocuments(profile.value.id, formData);
        alert('Document uploaded successfully');
        await fetchProfile();
        showUploadForm.value = false;
    } catch (err) {
        console.error('Failed to upload document:', err);
        alert(err.response?.data?.message || 'Failed to upload document');
    } finally {
        uploading.value = false;
        selectedFile.value = null;
        const fileInput = document.getElementById('document');
        if (fileInput) fileInput.value = '';
    }
};

const updateProfile = async () => {
    if (!isValidPhone(editData.value.phone)) {
        alert('Please enter a valid phone number');
        return;
    }

    updating.value = true;

    try {
        await updateProfessionalProfile(profile.value.id, {
            name: editData.value.name,
            phone: editData.value.phone,
            years_experience: parseInt(editData.value.years_experience),
            bio: editData.value.bio
        });

        alert('Profile updated successfully');
        editMode.value = false;
        await fetchProfile();
    } catch (err) {
        console.error('Failed to update profile:', err);
        alert(err.response?.data?.message || 'Failed to update profile');
    } finally {
        updating.value = false;
    }
};

const cancelEdit = () => {
    editData.value = {
        name: profile.value.name,
        phone: profile.value.phone,
        years_experience: profile.value.years_experience,
        bio: profile.value.bio || ''
    };
    editMode.value = false;
};
</script>

<style scoped>
.avatar-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: 500;
}
</style>