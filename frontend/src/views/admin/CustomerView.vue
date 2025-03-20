<template>
    <div>
        <h1>Manage Customers</h1>
        <div>
            <h2>Filters</h2>
            <div>
                <label for="status">Status:</label>
                <select v-model="filters.status" id="status" @change="applyFilters">
                    <option value="">All</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                </select>
            </div>

            <div>
                <label for="search">Search</label>
                <input type="text" id="search" v-model="filters.search" placeholder="Search by name, email, or pincode"
                    @input="debounceSearch">
            </div>

            <button @click="clearFilters">Clear Filters</button>
        </div>

        <div v-if="loading">Loading Customers</div>
        <div v-else-if="error">{{ error }}</div>

        <div v-if="filteredCustomers.length === 0">
            No customers found
        </div>
        <div v-else>
            <div v-for="customer in filteredCustomers" :key="customer.id">
                <h3>{{ customer.name }}</h3>
                <p>Email: {{ customer.email }}</p>
                <p>Phone: {{ customer.phone }}</p>
                <p>Address: {{ customer.address }}</p>
                <p>Pincode: {{ customer.pincode }}</p>
                <p>Registered On: {{ formatDate(customer.registered_on) }}</p>
                <p>Account Status: {{ customer.user.is_active ? 'Active' : 'Inactive' }}</p>
                <p>Total Requests: {{ customer.total_requests }}</p>
                <p>Completed Requests: {{ customer.completed_requests }}</p>

                <div>
                    <h4>Actions</h4>
                    <button v-if="customer.user.is_active" @click="updateStatus(customer.id, 'inactive')">Deactivate
                        Account</button>
                    <button v-else @click="updateStatus(customer.id, 'active')">
                        Activate Account
                    </button>
                </div>
                <hr>
            </div>
        </div>

    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
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

// Debounce timer
let searchTimeout = null;

// Method to debounce search input
const debounceSearch = () => {
    // Clear previous timeout
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }

    // Set a new timeout of 300ms before applying filters
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
        alert(`Customer account ${status === 'active' ? 'activated' : 'deactivated'} successfully`);
        // Refresh the list after updating status
        await adminStore.fetchCustomers();
    } catch (err) {
        console.error(`Failed to ${status} customer:`, err);
        alert(`Failed to ${status} customer account`);
    }
};
</script>