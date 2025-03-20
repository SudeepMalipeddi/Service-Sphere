<template>
    <div class="admin-dashboard">
        <h1>Admin Dashboard</h1>

        <div v-if="loading" class="text-center my-5">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
        <div v-else-if="dashboardStats">

            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body">
                            <h5 class="card-title">Total Customers</h5>
                            <p class="card-text display-4">{{ dashboardStats.total_counts.customers }}</p>
                            <p class="card-text">Active: {{ dashboardStats.active_counts.customers }}</p>
                        </div>
                    </div>
                </div>

                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body">
                            <h5 class="card-title">Total Professionals</h5>
                            <p class="card-text display-4">{{ dashboardStats.total_counts.professionals }}</p>
                            <p class="card-text">Active: {{ dashboardStats.active_counts.professionals }}</p>
                        </div>
                    </div>
                </div>

                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body">
                            <h5 class="card-title">Total Services</h5>
                            <p class="card-text display-4">{{ dashboardStats.total_counts.services }}</p>
                            <p class="card-text">Active: {{ dashboardStats.active_counts.services }}</p>
                        </div>
                    </div>
                </div>

                <div class="col-md-3">
                    <div class="card bg-warning text-dark">
                        <div class="card-body">
                            <h5 class="card-title">Pending Verifications</h5>
                            <p class="card-text display-4">{{ dashboardStats.pending_verifications }}</p>
                            <router-link v-if="dashboardStats.pending_verifications > 0"
                                to="/admin/professionals?verification_status=pending" class="btn btn-sm btn-dark mt-2">
                                View Pending
                            </router-link>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Recent Activity (Last 7 Days)</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-flex justify-content-around">
                                <div class="text-center">
                                    <h3>{{ dashboardStats.recent_activity.new_customers }}</h3>
                                    <p>New Customers</p>
                                </div>
                                <div class="text-center">
                                    <h3>{{ dashboardStats.recent_activity.new_professionals }}</h3>
                                    <p>New Professionals</p>
                                </div>
                                <div class="text-center">
                                    <h3>{{ dashboardStats.recent_activity.new_requests }}</h3>
                                    <p>New Requests</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Add this functionality when implementing service request functionality -->

                <!-- <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Service Request Status</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="requestStatusChartRef"></canvas>
                        </div>
                    </div>
                </div> -->
            </div>


            <div class="row">

                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Quick Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="list-group">
                                <router-link to="/admin/services" class="list-group-item list-group-item-action">
                                    Manage Services
                                </router-link>
                                <router-link to="/admin/professionals" class="list-group-item list-group-item-action">
                                    Manage Professionals
                                </router-link>
                                <router-link to="/admin/customers" class="list-group-item list-group-item-action">
                                    Manage Customers
                                </router-link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>


<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import Chart from 'chart.js/auto'

import { useAdminStore } from '@/stores/admin'

const adminStore = useAdminStore()
const dashboardStats = computed(() => adminStore.dashboardStats)
const loading = computed(() => adminStore.loading)

const statusChart = ref(null)
const requestStatusChartRef = ref(null);


const servicesChart = ref(null)
const popularServicesChartRef = ref(null)

// const renderRequestStatusChart = () => {
//     if (!dashboardStats.value || !dashboardStats.value.request_status) return

//     const statusData = dashboardStats.value.request_status
//     const labels = Object.keys(statusData)
//     const data = Object.values(statusData)

//     if (statusChart.value) {
//         statusChart.value.destroy()
//     }

//     statusChart.value = new Chart(requestStatusChartRef.value, {
//         type: 'pie',
//         data: {
//             labels,
//             datasets: [{
//                 data,
//                 backgroundColor: [
//                     '#4caf50', // completed/closed
//                     '#2196f3', // assigned
//                     '#ff9800', // requested
//                     '#f44336', // cancelled
//                     '#9c27b0'  // other statuses
//                 ]
//             }]
//         },
//         options: {
//             responsive: true,
//             plugins: {
//                 legend: {
//                     position: 'bottom'
//                 }
//             }
//         }
//     })
// }

const renderRequestStatusChart = async () => {
    await nextTick();

    if (!requestStatusChartRef.value || !dashboardStats.value?.request_status) return;

    if (statusChart.value) {
        statusChart.value.destroy();
        statusChart.value = null;
    }

    const ctx = requestStatusChartRef.value.getContext('2d');
    if (!ctx) return;

    const statusData = dashboardStats.value.request_status;
    const labels = Object.keys(statusData);
    const data = Object.values(statusData);

    statusChart.value = new Chart(ctx, {
        type: 'pie',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: ['#4caf50', '#2196f3', '#ff9800', '#f44336', '#9c27b0']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
};



// const renderPopularServicesChart = () => {
//     if (!dashboardStats.value || !dashboardStats.value.popular_services) return

//     const services = dashboardStats.value.popular_services
//     const labels = services.map(s => s.service_name)
//     const data = services.map(s => s.request_count)

//     if (servicesChart.value) {
//         servicesChart.value.destroy()
//     }

//     servicesChart.value = new Chart(popularServicesChartRef.value, {
//         type: 'bar',
//         data: {
//             labels,
//             datasets: [{
//                 label: 'Request Count',
//                 data,
//                 backgroundColor: '#3f51b5'
//             }]
//         },
//         options: {
//             responsive: true,
//             scales: {
//                 y: {
//                     beginAtZero: true,
//                     ticks: {
//                         precision: 0
//                     }
//                 }
//             }
//         }
//     })
// }

onMounted(async () => {
    await adminStore.fetchDashboardStats()
})

watch(dashboardStats, async () => {
    await nextTick();
    renderRequestStatusChart()
    // renderPopularServicesChart()
})
</script>
