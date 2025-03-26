<template>
    <div class="customer-profile-view">
        <h1>My Profile</h1>

        <div v-if="loading" class="text-center my-5">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-if="error" class="alert alert-danger">
            {{ error }}
        </div>

        <div v-if="profile && !loading" class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Profile Information</h5>
                <button v-if="!editMode" class="btn btn-primary" @click="editMode = true">
                    Edit Profile
                </button>
            </div>

            <div class="card-body" v-if="!editMode">
                <div class="row mb-2">
                    <div class="col-md-3 fw-bold">Name:</div>
                    <div class="col-md-9">{{ profile.name }}</div>
                </div>

                <div class="row mb-2">
                    <div class="col-md-3 fw-bold">Email:</div>
                    <div class="col-md-9">{{ profile.email }}</div>
                </div>

                <div class="row mb-2">
                    <div class="col-md-3 fw-bold">Phone:</div>
                    <div class="col-md-9">{{ profile.phone || 'Not provided' }}</div>
                </div>

                <div class="row mb-2">
                    <div class="col-md-3 fw-bold">Address:</div>
                    <div class="col-md-9">{{ profile.address || 'Not provided' }}</div>
                </div>

                <div class="row mb-2">
                    <div class="col-md-3 fw-bold">Pincode:</div>
                    <div class="col-md-9">{{ profile.pincode || 'Not provided' }}</div>
                </div>
            </div>

            <div v-else class="card-body">
                <form @submit.prevent="updateProfile">
                    <div class="mb-3">
                        <label for="name" class="form-label">Full Name</label>
                        <input type="text" class="form-control" id="name" v-model="editData.name" required>
                    </div>

                    <div class="mb-3">
                        <label for="phone" class="form-label">Phone Number</label>
                        <input type="tel" class="form-control" id="phone" v-model="editData.phone"
                            placeholder="Enter your phone number">
                    </div>

                    <div class="mb-3">
                        <label for="address" class="form-label">Address</label>
                        <textarea class="form-control" id="address" v-model="editData.address" rows="2"
                            placeholder="Enter your address"></textarea>
                    </div>

                    <div class="mb-3">
                        <label for="pincode" class="form-label">Pincode</label>
                        <input type="text" class="form-control" id="pincode" v-model="editData.pincode"
                            placeholder="Enter your pincode">
                    </div>

                    <div class="d-flex justify-content-end gap-2">
                        <button type="button" class="btn btn-secondary" @click="cancelEdit">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-primary" :disabled="updating">
                            {{ updating ? 'Saving...' : 'Save Changes' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getUser } from '@/utils/authutils';
import api from '@/api';

const profile = ref(null);
const loading = ref(true);
const error = ref(null);
const editMode = ref(false);
const updating = ref(false);

const editData = ref({
    name: '',
    phone: '',
    address: '',
    pincode: ''
});

const fetchProfile = async () => {
    loading.value = true;
    error.value = null;

    try {
        const user = getUser();
        if (!user?.customer_id) {
            error.value = "Customer profile not found";
            return;
        }

        const response = await api.get(`/customers/${user.customer_id}`);
        profile.value = response.data;

        editData.value = {
            name: profile.value?.name,
            phone: profile.value?.phone || '',
            address: profile.value?.address || '',
            pincode: profile.value?.pincode || ''
        };
    } catch (err) {
        console.error('Failed to fetch profile:', err);
        error.value = 'Failed to load profile data. Please try again.';
    } finally {
        loading.value = false;
    }
};


const updateProfile = async () => {
    updating.value = true;
    error.value = null;

    try {
        await api.put(`/customers/${profile.value.id}`, {
            name: editData.value.name,
            phone: editData.value.phone,
            address: editData.value.address,
            pincode: editData.value.pincode
        });

        const user = getUser();
        if (user.name !== editData.value.name) {
            user.name = editData.value.name;
            localStorage.setItem('user', JSON.stringify(user));
        }

        alert('Profile updated successfully');
        editMode.value = false;
        await fetchProfile();
    } catch (err) {
        console.error('Failed to update profile:', err);
        error.value = err.response?.data?.message || 'Failed to update profile. Please try again.';
    } finally {
        updating.value = false;
    }
};

const cancelEdit = () => {
    editData.value = {
        name: profile.value.name,
        phone: profile.value.phone || '',
        address: profile.value.address || '',
        pincode: profile.value.pincode || ''
    };
    editMode.value = false;
};

onMounted(() => {
    fetchProfile();
});
</script>