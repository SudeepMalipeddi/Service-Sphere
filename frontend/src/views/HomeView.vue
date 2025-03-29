<template>
  <div class="container">
    <div class="bg-primary text-white text-center py-5 mb-5">
      <div class="container">
        <h1 class="display-4">Service Sphere</h1>
        <p class="lead">Your one-stop platform for all household services</p>

        <div class="mt-4">
          <div v-if="!isAuthenticated" class="d-flex justify-content-center gap-3">
            <router-link to="/login" class="btn btn-light btn-lg">Login</router-link>
            <router-link to="/register" class="btn btn-outline-light btn-lg">Register</router-link>
          </div>

          <div v-else>
            <router-link :to="dashboardRoute" class="btn btn-light btn-lg">Go to Dashboard</router-link>
          </div>
        </div>
      </div>
    </div>


    <div class="container">
      <h2 class="text-center mb-4">Our Services</h2>

      <div v-if="loading" class="text-center my-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else-if="services.length === 0" class="text-center my-5">
        <p>No services available at the moment.</p>
      </div>
      <div v-else class="row">
        <div class="col-md-4 mb-4" v-for="service in services" :key="service.id">
          <div class="card h-100 card-hover">
            <div class="card-body">
              <h5 class="card-title">{{ service.name }}</h5>
              <p class="card-text">{{ service.description ? truncate(service.description, 120) : 'No\
                description available' }}</p>
              <div class="d-flex justify-content-between align-items-center">
                <span class="fw-bold">{{ formatPrice(service.base_price) }}</span>
                <span class="text-muted">{{ formatDuration(service.estimated_time) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { useServiceStore } from '@/stores/services';
import { computed, onMounted } from 'vue';
import { formatPrice, formatDuration, truncate } from '@/utils/formatters';

const authStore = useAuthStore();
const serviceStore = useServiceStore();

onMounted(() => {
  serviceStore.fetchServices({ show_inactive: false });
})

const dashboardRoute = computed(() => {
  if (authStore.userRole === 'admin') return '/admin'
  if (authStore.userRole === 'customer') return '/customer'
  if (authStore.userRole === 'professional') return '/professional'
  return '/';
})

const isAuthenticated = computed(() => authStore.isAuthenticated);
const userRole = computed(() => authStore.userRole);
const loading = computed(() => serviceStore.loading);
const services = computed(() => serviceStore.services);


</script>