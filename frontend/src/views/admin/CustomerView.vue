<template>
    <div class="admin-customers-view">
        <h1>Manage Customers</h1>

        <div class="card mb-4">
            <div class="card-body">
                <div class="row align-items-end">
                    <div class="col-md-4 mb-3 mb-md-0">
                        <label for="status" class="form-label">Status</label>
                        <select id="status" class="form-select" v-model="filters.status" @change="applyFilters">
                            <option value="">All</option>
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>
                    </div>

                    <div class="col-md-6 mb-3 mb-md-0">
                        <label for="search" class="form-label">Search</label>
                        <input type="text" id="search" class="form-control" v-model="filters.search"
                            @input="debounceSearch" placeholder="Search by name, email, or pincode">
                    </div>

                    <div class="col-md-2 text-end">
                        <button class="btn btn-secondary" @click="clearFilters">
                            Clear Filters
                        </button>
                    </div>
                </div>
            </div>
        </div>


        <div v-if="loading" class="text-center my-5">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">
            {{ error }}
        </div>


        <div v-else-if="filteredCustomers.length === 0" class="alert alert-info">
            No customers found matching your criteria.
        </div>

        <div v-else class="row">
            <div v-for="customer in filteredCustomers" :key="customer.id" class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">{{ customer.name }}</h5>
                        <span class="badge" :class="customer.user.is_active ? 'bg-success' : 'bg-danger'">
                            {{ customer.user.is_active ? 'Active' : 'Inactive' }}
                        </span>
                    </div>

                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-4 text-muted">Email:</div>
                            <div class="col-8">{{ customer.email }}</div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-4 text-muted">Phone:</div>
                            <div class="col-8">{{ customer.phone || 'Not provided' }}</div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-4 text-muted">Address:</div>
                            <div class="col-8">{{ customer.address || 'Not provided' }}</div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-4 text-muted">Pincode:</div>
                            <div class="col-8">{{ customer.pincode || 'Not provided' }}</div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-4 text-muted">Registered:</div>
                            <div class="col-8">{{ formatDate(customer.registered_on) }}</div>
                        </div>

                    </div>

                    <div class="card-footer text-end">
                        <button v-if="customer.user.is_active" class="btn btn-outline-danger"
                            @click="updateStatus(customer.id, 'inactive')">
                            Deactivate
                        </button>
                        <button v-else class="btn btn-outline-success" @click="updateStatus(customer.id, 'active')">
                            Activate
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAdminStore } from '@/stores/admin';
import { formatDate } from '@/utils/formatters';

const adminStore = useAdminStore();
const loading = computed(() => adminStore.loading);
const error = computed(() => adminStore.error);
const filteredCustomers = computed(() => adminStore.filteredCustomers);

const filters = ref({
    status: '',
    search: '',
});


let searchTimeout = null;


const debounceSearch = () => {

    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }


    searchTimeout = setTimeout(() => {
        applyFilters();
    }, 300);
};

onMounted(async () => {
    try {
        await adminStore.fetchCustomers();
    } catch (error) {
        console.error('Error fetching customers:', error);
    }
});

const applyFilters = async () => {
    adminStore.setCustomerFilters(filters.value);

    try {
        await adminStore.fetchCustomers();
    } catch (err) {
        console.error('Failed to fetch customers:', err);
    }
};

const clearFilters = () => {
    filters.value = {
        status: '',
        search: ''
    };
    adminStore.clearCustomerFilters();
    adminStore.fetchCustomers();
};

const updateStatus = async (id, status) => {
    try {
        await adminStore.updateCustomerActiveStatus(id, status);
        await adminStore.fetchCustomers();
    } catch (err) {
        console.error(`Failed to ${status} customer:`, err);
        alert(`Failed to ${status} customer account`);
    }
};
</script>