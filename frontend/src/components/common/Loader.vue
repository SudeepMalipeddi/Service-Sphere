<template>
    <div class="loader-container" v-if="loading">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>
</template>


<script setup>
import { defineProps } from 'vue'

defineProps({
    loading: {
        type: Boolean,
        default: false
    }
})
</script>

<style scoped>
.loader-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
}
</style>