<template>
    <div>
        <h1>Professional Profile</h1>

        <div v-if="loading">Loading profile data...</div>
        <div v-else-if="error">{{ error }}</div>

        <div v-if="profile">
            <div>
                <h2>Profile Information</h2>
                <p>Name: {{ profile.name }}</p>
                <p>Email: {{ profile.email }}</p>
                <p>Phone: {{ profile.phone }}</p>
                <p>Service: {{ profile.service_name }}</p>
                <p>Experience: {{ profile.years_experience }} years</p>
                <p>Verification Status: {{ profile.verification_status }}</p>
                <p v-if="profile.bio">Bio: {{ profile.bio }}</p>

                <div v-if="profile.verification_status === 'rejected'">
                    <p>Rejection Reason: {{ profile.verification_reason || 'No reason provided' }}</p>
                </div>

                <button @click="editMode = true">Edit Profile</button>
            </div>

            <div>
                <!-- {{ profile }} -->

                <div v-if="profile.documents_url && profile.documents_url.length > 0">
                    <h2>Verification Documents</h2>
                    <p>Uploaded Documents:</p>
                    <!-- <ul>
                        <li v-for="(doc, index) in profile.documents_url" :key="index">
                            <a :href="doc" target="_blank">View Document {{ index + 1 }}</a>
                        </li>
                    </ul> -->
                    <li v-for="(doc, index) in profile.documents_url" :key="index">
                        <a :href="doc" target="_blank">
                            View Document {{ index + 1 }}
                        </a>
                    </li>
                </div>

                <div v-else>
                    <div>
                        <h3>Upload Verification Document</h3>
                        <p>Please upload ID proof, certification, or experience documents.</p>

                        <form @submit.prevent="uploadDocument">
                            <div>
                                <label for="document">Select Document:</label>
                                <input type="file" id="document" @change="handleFileSelect"
                                    accept=".pdf,.jpg,.jpeg,.png" required>
                            </div>

                            <button type="submit" :disabled="uploading">
                                {{ uploading ? 'Uploading...' : 'Upload Document' }}
                            </button>
                        </form>
                    </div>
                </div>

                <!-- <div>
                    <h3>Upload Verification Document if not yet uploaded</h3>
                    <p>Please upload ID proof, certification, or experience documents.</p>

                    <form @submit.prevent="uploadDocument">
                        <div>
                            <label for="document">Select Document:</label>
                            <input type="file" id="document" @change="handleFileSelect" accept=".pdf,.jpg,.jpeg,.png"
                                required>
                        </div>

                        <button type="submit" :disabled="uploading">
                            {{ uploading ? 'Uploading...' : 'Upload Document' }}
                        </button>
                    </form>
                </div> -->
            </div>
        </div>

        <!-- Edit Profile Modal -->
        <div v-if="editMode && profile">
            <div>
                <h2>Edit Profile</h2>
                <form @submit.prevent="updateProfile">
                    <div>
                        <label for="name">Name:</label>
                        <input type="text" id="name" v-model="editData.name" required>
                    </div>

                    <div>
                        <label for="phone">Phone:</label>
                        <input type="tel" id="phone" v-model="editData.phone" required>
                    </div>

                    <div>
                        <label for="experience">Years of Experience:</label>
                        <input type="number" id="experience" v-model="editData.years_experience" min="0" required>
                    </div>

                    <div>
                        <label for="bio">Bio/Description:</label>
                        <textarea id="bio" v-model="editData.bio"
                            placeholder="Tell customers about your skills and experience"></textarea>
                    </div>

                    <button type="submit" :disabled="updating">
                        {{ updating ? 'Saving...' : 'Save Changes' }}
                    </button>
                    <button type="button" @click="editMode = false">Cancel</button>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getProfessional, updateProfessionalProfile, uploadDocuments } from '@/api/professional';
import { getUser } from '@/utils/authutils';
import { isValidPhone } from '@/utils/validators';

const loading = ref(true);
const error = ref(null);
const profile = ref(null);
const editMode = ref(false);
const uploading = ref(false);
const updating = ref(false);
const selectedFile = ref(null);

const editData = ref({
    name: '',
    phone: '',
    years_experience: 0,
    bio: ''
});

onMounted(async () => {
    await fetchProfile();
});

const fetchProfile = async () => {
    loading.value = true;
    error.value = null;

    try {
        const user = getUser();
        if (user.id && user.role === 'professional') {
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
        error.value = 'Failed to load profile data';
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
    error.value = null;

    try {
        const formData = new FormData();
        formData.append('document', selectedFile.value);

        await uploadDocuments(profile.value.id, formData);

        alert('Document uploaded successfully');
        await fetchProfile();
    } catch (err) {
        console.error('Failed to upload document:', err);
        error.value = err.response?.data?.message || 'Failed to upload document';
    } finally {
        uploading.value = false;
        selectedFile.value = null;
        // Reset file input
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
    error.value = null;

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
        error.value = err.response?.data?.message || 'Failed to update profile';
    } finally {
        updating.value = false;
    }
};
</script>