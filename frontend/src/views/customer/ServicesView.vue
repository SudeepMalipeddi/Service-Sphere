<template>
    <div class="customer-services-view">
        <h1>Available Services</h1>

        <!-- Search and filters -->
        <div class="card mb-4">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8 mb-3">
                        <label class="form-label">Search Services</label>
                        <div class="input-group">
                            <input type="text" class="form-control" placeholder="Search by service name or description"
                                v-model="searchQuery" @input="filterServices">
                            <button class="btn btn-outline-secondary" type="button" @click="clearSearch">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                    </div>

                    <div class="col-md-4 mb-3">
                        <label class="form-label">Sort By</label>
                        <select class="form-select" v-model="sortOption" @change="applySort">
                            <option value="name">Name</option>
                            <option value="price_low">Price (Low to High)</option>
                            <option value="price_high">Price (High to Low)</option>
                            <option value="time">Estimated Time</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <!-- Services grid -->
        <div v-if="loading" class="text-center my-5">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="filteredServices.length === 0" class="text-center my-5">
            <p>No services found matching your search.</p>
            <button class="btn btn-primary" @click="clearSearch">Clear Search</button>
        </div>

        <div v-else class="row">
            <div class="col-md-4 mb-4" v-for="service in filteredServices" :key="service.id">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">{{ service.name }}</h5>
                        <p class="card-text">{{ service.description || 'No description available' }}</p>

                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="fw-bold">{{ formatPrice(service.base_price) }}</span>
                            <span class="text-muted">{{ formatDuration(service.estimated_time) }}</span>
                        </div>

                        <button class="btn btn-primary w-100" @click="bookService(service)">
                            Book Now
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Booking Section (Displayed on the Page) -->
        <div v-if="selectedService" class="card mt-4">
            <div class="card-header">
                <h5>Book Service: {{ selectedService.name }}</h5>
            </div>
            <div class="card-body">
                <form @submit.prevent="createRequest">
                    <div class="mb-3">
                        <label for="scheduledDate" class="form-label">When do you need this service?</label>
                        <input type="datetime-local" class="form-control" id="scheduledDate"
                            v-model="bookingForm.scheduledDate" :min="minDate" required>
                        <div v-if="formErrors.scheduledDate" class="text-danger">
                            {{ formErrors.scheduledDate }}
                        </div>
                    </div>

                    <div class="mb-3">
                        <label for="remarks" class="form-label">Additional Information</label>
                        <textarea class="form-control" id="remarks" v-model="bookingForm.remarks" rows="3"
                            placeholder="Provide any additional details..."></textarea>
                    </div>

                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <p class="mb-0">Price: {{ formatPrice(selectedService.base_price) }}</p>
                            <small class="text-muted">Estimated time: {{ formatDuration(selectedService.estimated_time)
                            }}</small>
                        </div>

                        <div>
                            <button type="button" class="btn btn-secondary me-2" @click="cancelBooking">Cancel</button>
                            <button type="submit" class="btn btn-primary" :disabled="formSubmitting">
                                <span v-if="formSubmitting" class="spinner-border spinner-border-sm" role="status"
                                    aria-hidden="true"></span>
                                {{ formSubmitting ? 'Booking...' : 'Book Service' }}
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>

    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { formatPrice, formatDuration } from '@/utils/formatters';
import { useServiceStore } from '@/stores/services';
import { useRequestStore } from '@/stores/requests';

const serviceStore = useServiceStore();
const requestStore = useRequestStore();

const searchQuery = ref('');
const sortOption = ref('name');
const selectedService = ref(null);
const bookingForm = ref({ scheduledDate: '', remarks: '' });
const formErrors = ref({});
const formSubmitting = ref(false);

const loading = computed(() => serviceStore.loading);
const services = computed(() => serviceStore.availableServices);

const filteredServices = computed(() => {
    let result = services.value;
    if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(service =>
            service.name.toLowerCase().includes(query) || service.description?.toLowerCase().includes(query)
        );
    }
    return sortServices(result);
});

const minDate = computed(() => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 30);
    return now.toISOString().slice(0, 16);
});

const sortServices = (services) => {
    return [...services].sort((a, b) => {
        if (sortOption.value === 'name') return a.name.localeCompare(b.name);
        if (sortOption.value === 'price_low') return a.base_price - b.base_price;
        if (sortOption.value === 'price_high') return b.base_price - a.base_price;
        if (sortOption.value === 'time') return a.estimated_time - b.estimated_time;
        return 0;
    });
};

const bookService = (service) => {
    selectedService.value = service;
    bookingForm.value = { scheduledDate: '', remarks: '' };
    formErrors.value = {};
};

const cancelBooking = () => {
    selectedService.value = null;
};

const validateForm = () => {
    formErrors.value = {};

    if (!bookingForm.value.scheduledDate) {
        formErrors.value.scheduledDate = 'Please select a date and time';
        return false;
    }

    const selectedDate = new Date(bookingForm.value.scheduledDate);
    const minDateTime = new Date(minDate.value);

    if (selectedDate < minDateTime) {
        formErrors.value.scheduledDate = 'Selected time must be at least 30 minutes from now';
        return false;
    }

    return true;
};

const createRequest = async () => {
    if (!validateForm()) return;

    formSubmitting.value = true;

    try {
        const localDate = new Date(bookingForm.value.scheduledDate);
        const requestData = {
            service_id: selectedService.value.id,
            scheduled_date: localDate.toISOString(),
            remarks: bookingForm.value.remarks
        };

        await requestStore.createNewRequest(requestData);

        console.log('Service request created successfully');
        window.location.href = '/customer/requests';
    } catch (error) {
        console.error('Create request error:', error);
        alert('Failed to create service request');
    } finally {
        formSubmitting.value = false;
    }
};

onMounted(() => {
    serviceStore.fetchServices({
        show_inactive: false,
        show_unavailable: false
    });
});
</script>
