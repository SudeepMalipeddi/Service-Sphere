<template>
    <footer class="footer mt-auto py-3 bg-light">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5>Service Sphere</h5>
                    <p class="text-muted">Your one-stop platform for all household services</p>
                </div>
                <div class="col-md-3">
                </div>
                <div class="col-md-3">
                    <h5>Contact</h5>
                    <address>
                        <p class="mb-0">Email: admin@example.com</p>
                        <p class="mb-0">Phone: +91 1234567890</p>
                    </address>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-12 text-center">
                    <p class="text-muted">&copy; {{ currentYear }} Service Sphere</p>
                </div>
            </div>
        </div>
    </footer>
</template>

<script setup>

import { computed } from 'vue'


const currentYear = computed(() => {
    return new Date().getFullYear()
})

</script>