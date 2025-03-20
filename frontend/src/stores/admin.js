import { defineStore } from "pinia";
import {
    getDashboardStats,
    getAdminProfessionals,
    updateProfessionalStatus,
    getAdminCustomers,
    updateCustomerStatus
} from '@/api/admin'
import { verifyProfessional } from "@/api/professional";

export const useAdminStore = defineStore('admin', {
    state: () => ({
        dashboardStats: null,
        professionals: [],
        customers: [],
        loading: false,
        error: null,
        professionalFilters: {
            status: null,
            service_id: null,
            verification_status: null
        },
        customerFilters: {
            status: null,
            search: ''
        }
    }),
    getters: {
        pendingVerifications: (state) => {
            return state.dashboardStats?.pending_verifications || 0
        },
        filteredProfessionals: (state) => {
            if (!state.professionals.length) return []

            return state.professionals.filter(professional => {


                // Filter by active status

                const userIsActive = professional.user?.is_active;

                if (state.professionalFilters.status &&
                    userIsActive !== (state.professionalFilters.status === 'active')) {
                    return false
                }

                if (state.professionalFilters.service_id &&
                    professional.service_id !== parseInt(state.professionalFilters.service_id)) {
                    return false
                }


                if (state.professionalFilters.verification_status &&
                    professional.verification_status !== state.professionalFilters.verification_status) {
                    return false
                }

                return true
            })
        },
        filteredCustomers: (state) => {
            if (!state.customers.length) return []

            return state.customers.filter(customer => {
                // Filter by active status
                if (state.customerFilters.status &&
                    customer.user?.is_active !== (state.customerFilters.status === 'active')) {
                    return false
                }

                // Filter by search term
                if (state.customerFilters.search) {
                    const search = state.customerFilters.search.toLowerCase()
                    const nameMatch = customer.name?.toLowerCase().includes(search)
                    const emailMatch = customer.email?.toLowerCase().includes(search)
                    const pincodeMatch = customer.pincode?.toLowerCase().includes(search)

                    return nameMatch || emailMatch || pincodeMatch
                }

                return true
            })
        }
    },
    actions: {
        async fetchDashboardStats() {
            this.loading = true
            this.error = null

            try {
                const response = await getDashboardStats()
                this.dashboardStats = response.data
                return response.data
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to fetch dashboard statistics'
                throw error
            } finally {
                this.loading = false
            }
        },
        async fetchProfessionals(params = {}) {
            this.loading = true
            this.error = null

            // Merge filter options with params
            if (this.professionalFilters.status) {
                params.status = this.professionalFilters.status
            }

            if (this.professionalFilters.service_id) {
                params.service_id = this.professionalFilters.service_id
            }

            if (this.professionalFilters.verification_status) {
                params.verification_status = this.professionalFilters.verification_status
            }

            try {
                const response = await getAdminProfessionals(params)
                this.professionals = response.data.professionals
                return response.data.professionals
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to fetch professionals'
                throw error
            } finally {
                this.loading = false
            }
        },
        async updateProfessionalActiveStatus(professional_id, status) {
            this.loading = true
            this.error = null

            try {
                const response = await updateProfessionalStatus({ professional_id, status })

                // Update professional in list
                const index = this.professionals.findIndex(p => p.id === professional_id)
                if (index !== -1) {
                    this.professionals[index] = response.data.professional
                }

                return response.data.professional
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to update professional status'
                throw error
            } finally {
                this.loading = false
            }
        },
        async verifyProfessionalStatus(professional_id, action, message) {
            this.loading = true
            this.error = null

            try {
                const response = await verifyProfessional(professional_id, { action, message })

                // Update professional in list
                const index = this.professionals.findIndex(p => p.id === professional_id)
                if (index !== -1) {
                    this.professionals[index] = response.data.professional
                }

                // Update pending verifications count
                if (this.dashboardStats && this.dashboardStats.pending_verifications > 0) {
                    this.dashboardStats.pending_verifications--
                }

                return response.data.professional
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to verify professional'
                throw error
            } finally {
                this.loading = false
            }
        },
        async fetchCustomers(params = {}) {
            this.loading = true
            this.error = null

            // Merge filter options with params
            if (this.customerFilters.status) {
                params.status = this.customerFilters.status
            }

            if (this.customerFilters.search) {
                params.search = this.customerFilters.search
            }

            try {
                const response = await getAdminCustomers(params)
                this.customers = response.data.customers
                return response.data.customers
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to fetch customers'
                throw error
            } finally {
                this.loading = false
            }
        },

        async updateCustomerActiveStatus(customer_id, status) {
            this.loading = true
            this.error = null

            try {
                const response = await updateCustomerStatus({ customer_id, status })

                // Update customer in list
                const index = this.customers.findIndex(c => c.id === customer_id)
                if (index !== -1) {
                    this.customers[index] = response.data.customer
                }

                return response.data.customer
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to update customer status'
                throw error
            } finally {
                this.loading = false
            }
        },

        setProfessionalFilters(filters) {
            this.professionalFilters = { ...this.professionalFilters, ...filters }
        },

        setCustomerFilters(filters) {
            this.customerFilters = { ...this.customerFilters, ...filters }
        },

        clearProfessionalFilters() {
            this.professionalFilters = {
                status: null,
                service_id: null,
                verification_status: null
            }
        },

        clearCustomerFilters() {
            this.customerFilters = {
                status: null,
                search: ''
            }
        }
    }
})
