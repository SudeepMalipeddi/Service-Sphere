<template>
    <div class="register-view">
        <h1 class="text-center mb-4">Register</h1>

        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-body">
                        <form @submit.prevent="handleRegister">
                            <div class="mb-3">
                                <label class="form-label">I want to register as:</label>
                                <div class="btn-group w-100" role="group">
                                    <input type="radio" class="btn-check" name="role" id="role-customer"
                                        value="customer" v-model="userData.role">
                                    <label class="btn btn-outline-primary" for="role-customer">Customer</label>

                                    <input type="radio" class="btn-check" name="role" id="role-professional"
                                        value="professional" v-model="userData.role">
                                    <label class="btn btn-outline-primary" for="role-professional">Service
                                        Professional</label>
                                </div>
                                <div v-if="errors.role" class="text-danger">
                                    {{ errors.role }}
                                </div>
                            </div>

                            <!-- Basic information -->
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="name" class="form-label">Name</label>
                                    <input type="text" class="form-control" id="name" v-model="userData.name" required
                                        :disabled="loading">
                                    <div v-if="errors.name" class="text-danger">
                                        {{ errors.name }}
                                    </div>
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label for="email" class="form-label">Email address</label>
                                    <input type="email" class="form-control" id="email" v-model="userData.email"
                                        required :disabled="loading">
                                    <div v-if="errors.email" class="text-danger">
                                        {{ errors.email }}
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password"
                                        v-model="userData.password" required :disabled="loading">
                                    <div v-if="errors.password" class="text-danger">
                                        {{ errors.password }}
                                    </div>
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label for="phone" class="form-label">Phone</label>
                                    <input type="tel" class="form-control" id="phone" v-model="userData.phone"
                                        :disabled="loading">
                                    <div v-if="errors.phone" class="text-danger">
                                        {{ errors.phone }}
                                    </div>
                                </div>
                            </div>

                            <!-- Customer-specific fields -->
                            <div v-if="userData.role === 'customer'" class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="address" class="form-label">Address</label>
                                    <input type="text" class="form-control" id="address" v-model="userData.address"
                                        :disabled="loading">
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label for="pincode" class="form-label">PIN Code</label>
                                    <input type="text" class="form-control" id="pincode" v-model="userData.pincode"
                                        :disabled="loading">
                                    <div v-if="errors.pincode" class="text-danger">
                                        {{ errors.pincode }}
                                    </div>
                                </div>
                            </div>

                            <!-- Professional-specific fields -->
                            <div v-if="userData.role === 'professional'" class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="service_id" class="form-label">Service Type</label>
                                    <select class="form-select" id="service_id" v-model="userData.service_id" required
                                        :disabled="loading">
                                        <option value="" disabled>Select a service</option>
                                        <option v-for="service in services" :key="service.id" :value="service.id">
                                            {{ service.name }}
                                        </option>
                                    </select>
                                    <div v-if="errors.service_id" class="text-danger">
                                        {{ errors.service_id }}
                                    </div>
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label for="years_experience" class="form-label">Years of Experience</label>
                                    <input type="number" class="form-control" id="years_experience"
                                        v-model="userData.years_experience" min="0" :disabled="loading">
                                </div>
                            </div>

                            <div v-if="userData.role === 'professional'" class="mb-3">
                                <label for="bio" class="form-label">Bio/Description</label>
                                <textarea class="form-control" id="bio" v-model="userData.bio" rows="3"
                                    :disabled="loading"></textarea>
                            </div>

                            <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                                <span v-if="loading" class="spinner-border spinner-border-sm" role="status"
                                    aria-hidden="true"></span>
                                {{ loading ? 'Registering...' : 'Register' }}
                            </button>
                        </form>

                        <div class="mt-3 text-center">
                            <p>Already have an account? <router-link to="/login">Login</router-link></p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useServiceStore } from '@/stores/services'
import { isValidEmail, isValidPassword, isValidPhone, isValidPincode } from '@/utils/validators'

const authStore = useAuthStore()
const serviceStore = useServiceStore()

const userData = ref({
    role: 'customer',
    name: '',
    email: '',
    password: '',
    phone: '',
    address: '',
    pincode: '',
    service_id: null, // made service_id null
    years_experience: 0,
    bio: ''
})

const errors = ref({})
const loading = computed(() => authStore.loading)
const services = computed(() => serviceStore.services)

const validateForm = () => {
    errors.value = {}

    if (!userData.value.role) {
        errors.value.role = 'Please select a role'
    }

    if (!userData.value.name) {
        errors.value.name = 'Name is required'
    }

    if (!userData.value.email) {
        errors.value.email = 'Email is required'
    } else if (!isValidEmail(userData.value.email)) {
        errors.value.email = 'Invalid email format'
    }

    if (!userData.value.password) {
        errors.value.password = 'Password is required'
    } else if (!isValidPassword(userData.value.password)) {
        errors.value.password = 'Password must be at least 6 characters'
    }

    if (userData.value.phone && !isValidPhone(userData.value.phone)) {
        errors.value.phone = 'Invalid phone number format'
    }

    if (userData.value.role === 'customer' && userData.value.pincode && !isValidPincode(userData.value.pincode)) {
        errors.value.pincode = 'PIN code must be 6 digits'
    }

    if (userData.value.role === 'professional' && !userData.value.service_id) {
        errors.value.service_id = 'Please select a service'
    }

    return Object.keys(errors.value).length === 0
}

const handleRegister = async () => {
    if (!validateForm()) return

    try {
        await authStore.registerUser(userData.value)
        // Redirect will be handled in the store
    } catch (error) {
        console.error('Registration error:', error)
    }
}

onMounted(() => {
    serviceStore.fetchServices({ show_inactive: false })
})
</script>
