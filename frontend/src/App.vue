<template>

  <div id="app">
    <Navbar v-if="isAuthenticated" />

    <div class="container mt-4">

      <router-view />
    </div>

    <Footer />
  </div>

</template>



<script setup>
import Navbar from '@/components/common/Navbar.vue';
import Footer from './components/common/Footer.vue';

import { useAuthStore } from './stores/auth';
import { computed, onMounted } from 'vue';

const authStore = useAuthStore();

const isAuthenticated = computed(() => authStore.isAuthenticated)
const errorMessage = computed(() => authStore.errorMessage)
const successMessage = computed(() => authStore.successMessage)

const clearError = authStore.clearError
const clearSuccess = authStore.clearSuccess
const checkAuth = authStore.checkAuth

onMounted(() => {
  checkAuth()
})


</script>

<style></style>