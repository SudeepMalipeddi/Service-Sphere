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
            showInactive: false,
            showUnavailable: false
        }
    }),
    getters: {
        serviceById: (state) => (id) => {
            return state.services.find(service => service.id === id)
        },
        filteredServices: (state) => {
            if (!state.services.length) return []

            return state.services.filter(service => {

                if (!state.filterOptions.showInactive && !service.is_active) {
                    return false
                }

                if (!state.filterOptions.showUnavailable && !service.has_verified_professionals) {
                    return false
                }

                if (state.searchQuery) {
                    const query = state.searchQuery.toLowerCase()
                    const nameMatch = service.name.toLowerCase().includes(query)
                    const descMatch = service.description?.toLowerCase().includes(query)

                    return nameMatch || descMatch
                }

                return true
            })
        },
        availableServices: (state) => {
            return state.services.filter(service =>
                service.is_active && service.has_verified_professionals
            )
        }
    },
    actions: {
        async fetchServices(params = {}) {
            this.loading = true
            this.error = null

            const showInactive = params.show_inactive !== undefined ? params.show_inactive : this.filterOptions.showInactive
            const showUnavailable = params.show_unavailable !== undefined ? params.show_unavailable : this.filterOptions.showUnavailable

            try {
                const queryParams = {
                    ...params,
                    show_inactive: showInactive,
                    show_unavailable: showUnavailable
                }

                const response = await getServices(queryParams)
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
                const response = await getServiceById(id)
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
                const index = this.services.findIndex(s => s.id === id)
                if (index !== -1) {
                    this.services[index] = response.data.service
                }

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
                this.services = this.services.filter(s => s.id !== id)

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
                showInactive: false,
                showUnavailable: false
            }
        }
    }
})