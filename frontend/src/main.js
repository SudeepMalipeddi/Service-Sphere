// import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import axios from 'axios'
axios.defaults.baseURL = 'http://localhost:5000/api'

import { useAuthStore } from './stores/auth'
import { useServiceStore } from './stores/services'
import { useNotificationsStore } from './stores/notifications'
import { useAdminStore } from './stores/admin'
import { useRequestStore } from './stores/requests'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

const initializeStores = async () => {
    const authStore = useAuthStore()
    const serviceStore = useServiceStore()
    const notificationStore = useNotificationsStore()
    const adminStore = useAdminStore()
    const requestStore = useRequestStore()

    try {
        await authStore.checkAuth()
        if (authStore.isAuthenticated && authStore.token) {
            serviceStore.fetchServices({ show_inactive: false })
            if (authStore.isAdmin) {
                adminStore.fetchDashboardStats()
            }
        }
    } catch (error) {
        console.error('Error initializing auth:', error)
    }
    return {
        authStore,
        serviceStore,
        notificationStore,
        adminStore,
        requestStore
    }
}
const initApp = async () => {
    const stores = await initializeStores()
    if (import.meta.env.DEV) {
        window.$stores = stores
    }
    app.mount('#app')
}
initApp()