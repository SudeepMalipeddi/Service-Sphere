import { defineStore } from "pinia";
import { getServices, getService as getServiceById, createService, updateService, deleteService } from "@/api/services";

export const useServiceStore = defineStore('service', {
    state: () => ({
        services: [],
        currentService: null,
        loading: false,
        error: null,
        searchQuery: '',
        filterOptions: {
            pincode: '',
            showInactive: false
        }
    }),
    getters: {
        serviceById: (state) => (id) => {
            return state.services.find(service => service.id === id)
        },
        filteredServices: (state) => {
            if (!state.services.length) return []

            return state.services.filter(service => {
                // Filter by active status
                if (!state.filterOptions.showInactive && !service.is_active) {
                    return false
                }

                // Filter by search query (case insensitive)
                if (state.searchQuery) {
                    const query = state.searchQuery.toLowerCase()
                    const nameMatch = service.name.toLowerCase().includes(query)
                    const descMatch = service.description?.toLowerCase().includes(query)

                    return nameMatch || descMatch
                }

                return true
            })
        },
        activeServices: (state) => {
            return state.services.filter(service => service.is_active)
        }
    },
    actions: {
        async fetchServices(params = {}) {
            this.loading = true
            this.error = null
            try {
                const response = await getServices(params)
                this.services = response.data.services
                return response.data.services
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to fetch services'
                throw error
            } finally {
                this.loading = false
            }
        },
        async fetchServiceById(id) {
            this.loading = true
            this.error = null

            try {
                const response = await getService(id)
                this.currentService = response.data.service
                return response.data.service
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to fetch service'
                throw error
            } finally {
                this.loading = false
            }
        },
        async createNewService(serviceData) {
            this.loading = true
            this.error = null

            try {
                const response = await createService(serviceData)
                // Add to services array
                this.services.push(response.data.service)
                return response.data.service
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to create service'
                throw error
            } finally {
                this.loading = false
            }
        },
        async updateExistingService(id, serviceData) {
            this.loading = true
            this.error = null

            try {
                const response = await updateService(id, serviceData)

                // Update in services array
                const index = this.services.findIndex(s => s.id === id)
                if (index !== -1) {
                    this.services[index] = response.data.service
                }

                // Update current service if it's the same
                if (this.currentService && this.currentService.id === id) {
                    this.currentService = response.data.service
                }

                return response.data.service
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to update service'
                throw error
            } finally {
                this.loading = false
            }
        },

        async removeService(id) {
            this.loading = true
            this.error = null

            try {
                await deleteService(id)

                // Remove from services array
                this.services = this.services.filter(s => s.id !== id)

                // Clear current service if it's the same
                if (this.currentService && this.currentService.id === id) {
                    this.currentService = null
                }

                return true
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to delete service'
                throw error
            } finally {
                this.loading = false
            }
        },

        setSearchQuery(query) {
            this.searchQuery = query
        },

        setFilterOptions(options) {
            this.filterOptions = { ...this.filterOptions, ...options }
        },

        clearFilters() {
            this.searchQuery = ''
            this.filterOptions = {
                pincode: '',
                showInactive: false
            }
        }
    }
})