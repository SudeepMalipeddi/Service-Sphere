<template>
    <div class="admin-service-management-view">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>Manage Services</h1>
            <button class="btn btn-primary" @click="openServiceForm()">
                <i class="bi bi-plus-circle me-2"></i> Add New Service
            </button>
        </div>

        <div v-if="deleteError" class="alert alert-danger alert-dismissible fade show" role="alert">
            {{ deleteError }}
            <button type="button" class="btn-close" @click="deleteError = ''"></button>
        </div>

        <div class="card mb-4">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" id="showInactive" v-model="showInactive">
                            <label class="form-check-label" for="showInactive">Show Inactive Services</label>
                        </div>
                    </div>

                    <div class="col-md-6 mb-3">
                        <div class="input-group">
                            <input type="text" class="form-control" placeholder="Search services..."
                                v-model="searchQuery">
                            <button class="btn btn-outline-secondary" @click="searchQuery = ''">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                    </div>
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

                <div v-else-if="filteredServices.length === 0" class="text-center my-5">
                    <p>No services found matching the criteria.</p>
                </div>

                <div v-else class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Base Price</th>
                                <th>Estimated Time</th>
                                <th>Description</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="service in filteredServices" :key="service.id">
                                <td>{{ service.id }}</td>
                                <td>{{ service.name }}</td>
                                <td>{{ formatPrice(service.base_price) }}</td>
                                <td>{{ formatDuration(service.estimated_time) }}</td>
                                <td>{{ service.description }}</td>
                                <td>
                                    <span :class="service.is_active ? 'badge bg-success' : 'badge bg-danger'">
                                        {{ service.is_active ? 'Active' : 'Inactive' }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-info me-2" @click="openServiceForm(service)">
                                        Edit
                                    </button>
                                    <button class="btn btn-sm"
                                        :class="service.is_active ? 'btn-warning' : 'btn-success'"
                                        @click="toggleServiceStatus(service)">
                                        {{ service.is_active ? 'Deactivate' : 'Activate' }}
                                    </button>
                                    <button class="btn btn-sm btn-danger" @click="deleteService(service.id)">
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        {{ }}

        <div v-if="showServiceForm" class="card mt-4">
            <div class="card-body">
                <h5>{{ isEditing ? "Edit Service" : "Add New Service" }}</h5>
                <form @submit.prevent="saveService">
                    <div class="mb-3">
                        <label class="form-label">Service Name</label>
                        <input type="text" class="form-control" v-model="serviceForm.name" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Base Price (₹)</label>
                        <input type="number" class="form-control" v-model="serviceForm.base_price" min="0" step="0.01"
                            required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Estimated Time (minutes)</label>
                        <input type="number" class="form-control" v-model="serviceForm.estimated_time" min="1" required>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Description</label>
                        <textarea class="form-control" v-model="serviceForm.description" rows="3"></textarea>
                    </div>

                    <div class="mb-3 form-check">
                        <input type="checkbox" class="form-check-input" v-model="serviceForm.is_active">
                        <label class="form-check-label">Active</label>
                    </div>

                    <div class="d-flex justify-content-end">
                        <button type="button" class="btn btn-secondary me-2" @click="closeServiceForm">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-primary">
                            {{ isEditing ? "Update Service" : "Add Service" }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, computed, onMounted } from "vue";
import { useServiceStore } from "@/stores/services";
import { useAdminStore } from "@/stores/admin";
import { formatPrice, formatDuration } from "@/utils/formatters";
import { isValidPrice } from "@/utils/validators";



const serviceStore = useServiceStore();
const adminStore = useAdminStore();
const loading = ref(false);

const deleteError = ref("");

const searchQuery = ref("");
const showInactive = ref(false);
const isEditing = ref(false);
const selectedService = ref(null);
const formErrors = ref({});
const formSubmitting = ref(false);
const showServiceForm = ref(false);


const serviceForm = ref({
    name: "",
    base_price: 0,
    estimated_time: 60,
    description: "",
    is_active: true
});


onMounted(async () => {
    await Promise.all([
        serviceStore.fetchServices({ show_inactive: true }),
        adminStore.fetchProfessionals()
    ]);
});


const filteredServices = computed(() => {
    return serviceStore.services.filter(service => {
        if (!showInactive.value && !service.is_active) return false;
        if (searchQuery.value) {
            const query = searchQuery.value.toLowerCase();
            return service.name.toLowerCase().includes(query) ||
                service.description?.toLowerCase().includes(query);
        }
        return true;
    });
});

const openServiceForm = (service = null) => {
    formErrors.value = {};

    if (service) {
        isEditing.value = true;
        selectedService.value = service;
        serviceForm.value = { ...service };
    } else {
        isEditing.value = false;
        selectedService.value = null;
        serviceForm.value = {
            name: "",
            base_price: 0,
            estimated_time: 60,
            description: "",
            is_active: true
        };
    }
    showServiceForm.value = true;
};


const closeServiceForm = () => {
    showServiceForm.value = false;
};

const validateForm = () => {
    formErrors.value = {};

    if (!serviceForm.value.name) {
        formErrors.value.name = "Service name is required";
    }
    if (!isValidPrice(serviceForm.value.base_price)) {
        formErrors.value.base_price = "Base price must be a positive number";
    }
    if (!serviceForm.value.estimated_time || serviceForm.value.estimated_time <= 0) {
        formErrors.value.estimated_time = "Estimated time must be a positive number";
    }

    return Object.keys(formErrors.value).length === 0;
};


const saveService = async () => {
    if (!validateForm()) return;

    formSubmitting.value = true;

    try {
        if (isEditing.value) {
            await serviceStore.updateExistingService(selectedService.value.id, serviceForm.value);

        } else {
            await serviceStore.createNewService(serviceForm.value);

        }
        closeServiceForm();
    } catch (error) {
        console.error("Save service error:", error);

    } finally {
        formSubmitting.value = false;
    }
};


const toggleServiceStatus = async (service) => {
    try {
        await serviceStore.updateExistingService(service.id, { is_active: !service.is_active });

    } catch (error) {
        console.error("Toggle service status error:", error);

    }
};

onMounted(async () => {
    loading.value = true;
    try {
        await Promise.all([
            serviceStore.fetchServices({ show_inactive: true }),
            adminStore.fetchProfessionals()
        ]);
    } finally {
        loading.value = false;
    }
})


const deleteService = async (id) => {
    formSubmitting.value = true;

    deleteError.value = "";
    try {
        await serviceStore.removeService(id);

    } catch (error) {
        deleteError.value = error.response?.data?.message || "An error occurred while deleting the service.";
        console.error("Delete service error:", error);

    } finally {
        formSubmitting.value = false;
    }
};


const getServiceProfessionalCount = (serviceId) => {
    return adminStore.professionals.filter(p => p.service_id === serviceId).length;
};
</script>
