<template>
    <div class="admin-dashboard">
        <h1>Admin Dashboard</h1>

        <div v-if="loading" class="text-center my-5">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="dashboardStats" class="dashboard-content">

            <div class="row g-4 mb-4">

                <div class="col-md-3">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body text-center">
                            <div class="icon-wrapper bg-light-primary mb-3">
                                <i class="bi bi-people text-primary"></i>
                            </div>
                            <h5 class="card-title">Customers</h5>
                            <h2 class="mb-1">{{ dashboardStats.total_counts.customers }}</h2>
                            <p class="text-muted small mb-0">
                                Active: {{ dashboardStats.active_counts.customers }}
                            </p>
                        </div>
                        <div class="card-footer bg-transparent border-0 text-center">
                            <router-link to="/admin/customers" class="btn btn-sm btn-outline-primary">
                                Manage Customers
                            </router-link>
                        </div>
                    </div>
                </div>


                <div class="col-md-3">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body text-center">
                            <div class="icon-wrapper bg-light-success mb-3">
                                <i class="bi bi-briefcase text-success"></i>
                            </div>
                            <h5 class="card-title">Professionals</h5>
                            <h2 class="mb-1">{{ dashboardStats.total_counts.professionals }}</h2>
                            <p class="text-muted small mb-0">
                                Active: {{ dashboardStats.active_counts.professionals }}
                            </p>
                        </div>
                        <div class="card-footer bg-transparent border-0 text-center">
                            <router-link to="/admin/professionals" class="btn btn-sm btn-outline-success">
                                Manage Professionals
                            </router-link>
                        </div>
                    </div>
                </div>


                <div class="col-md-3">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body text-center">
                            <div class="icon-wrapper bg-light-info mb-3">
                                <i class="bi bi-tools text-info"></i>
                            </div>
                            <h5 class="card-title">Services</h5>
                            <h2 class="mb-1">{{ dashboardStats.total_counts.services }}</h2>
                            <p class="text-muted small mb-0">
                                Active: {{ dashboardStats.active_counts.services }}
                            </p>
                        </div>
                        <div class="card-footer bg-transparent border-0 text-center">
                            <router-link to="/admin/services" class="btn btn-sm btn-outline-info">
                                Manage Services
                            </router-link>
                        </div>
                    </div>
                </div>


                <div class="col-md-3">
                    <div class="card h-100 border-0 shadow-sm">
                        <div class="card-body text-center">
                            <div class="icon-wrapper bg-light-warning mb-3">
                                <i class="bi bi-clock-history text-warning"></i>
                            </div>
                            <h5 class="card-title">Pending Verifications</h5>
                            <h2 class="mb-1">{{ dashboardStats.pending_verifications }}</h2>
                            <p class="text-muted small mb-0">
                                Awaiting review
                            </p>
                        </div>
                        <div class="card-footer bg-transparent border-0 text-center">
                            <router-link v-if="dashboardStats.pending_verifications > 0"
                                to="/admin/professionals?verification_status=pending"
                                class="btn btn-sm btn-outline-warning">
                                Review Pending
                            </router-link>
                            <button v-else class="btn btn-sm btn-outline-secondary" disabled>
                                No Pending Verifications
                            </button>
                        </div>
                    </div>
                </div>
            </div>


            <div class="row g-4">

                <div class="col-md-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header bg-transparent">
                            <h5 class="mb-0">Recent Activity (Last 7 Days)</h5>
                        </div>
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-4">
                                    <div class="activity-stat">
                                        <h3 class="activity-number">{{ dashboardStats.recent_activity.new_customers }}
                                        </h3>
                                        <p class="activity-label">New Customers</p>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="activity-stat">
                                        <h3 class="activity-number">{{ dashboardStats.recent_activity.new_professionals
                                            }}</h3>
                                        <p class="activity-label">New Professionals</p>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="activity-stat">
                                        <h3 class="activity-number">{{ dashboardStats.recent_activity.new_requests }}
                                        </h3>
                                        <p class="activity-label">New Requests</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>


                <div class="col-md-6">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header bg-transparent">
                            <h5 class="mb-0">Service Request Status</h5>
                        </div>
                        <div class="card-body">
                            <canvas ref="requestStatusChartRef" height="200"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import Chart from 'chart.js/auto';
import { useAdminStore } from '@/stores/admin';

const adminStore = useAdminStore();
const dashboardStats = computed(() => adminStore.dashboardStats);
const loading = computed(() => adminStore.loading);

const statusChart = ref(null);
const requestStatusChartRef = ref(null);

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


    const chartColors = [
        'rgba(75, 192, 192, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(153, 102, 255, 0.7)'
    ];

    statusChart.value = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: chartColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                }
            },
            cutout: '65%'
        }
    });
};

onMounted(async () => {
    await adminStore.fetchDashboardStats();
});

watch(dashboardStats, async () => {
    await nextTick();
    renderRequestStatusChart();
});
</script>

<style scoped>
.icon-wrapper {
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    margin: 0 auto;
}

.icon-wrapper i {
    font-size: 24px;
}

.bg-light-primary {
    background-color: rgba(13, 110, 253, 0.15);
}

.bg-light-success {
    background-color: rgba(25, 135, 84, 0.15);
}

.bg-light-info {
    background-color: rgba(13, 202, 240, 0.15);
}

.bg-light-warning {
    background-color: rgba(255, 193, 7, 0.15);
}

.activity-stat {
    padding: 15px 0;
}

.activity-number {
    font-size: 32px;
    font-weight: 500;
    margin-bottom: 5px;
    color: #333;
}

.activity-label {
    color: #666;
    margin-bottom: 0;
}
</style>