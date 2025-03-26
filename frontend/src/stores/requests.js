import { defineStore } from "pinia";
import {
    getServiceRequests,
    getServiceRequest,
    createServiceRequest,
    updateServiceRequest,
    cancelServiceRequest,
    serviceRequestAction,
    getAvailableRequests,
    submitReview,
    updateReview,
    getRequestReviews,
} from "@/api/serviceRequest"



export const useRequestStore = defineStore("requests", {
    state: () => ({
        requests: [],
        currentRequest: null,
        availableRequests: [],
        loading: false,
        error: null,
        filterOptions: {
            status: null,
            dateFrom: null,
            dateTo: null
        }
    }),

    getters: {
        requestById: (state) => (id) => {
            return state.requests.find(request => request.id === id)
        },

        filteredRequests: (state) => {
            if (!state.requests.length) return []

            return state.requests.filter(request => {

                if (state.filterOptions.status && request.status !== state.filterOptions.status) {
                    return false
                }


                if (state.filterOptions.dateFrom) {
                    const fromDate = new Date(state.filterOptions.dateFrom)
                    const requestDate = new Date(request.request_date)
                    if (requestDate < fromDate) return false
                }

                if (state.filterOptions.dateTo) {
                    const toDate = new Date(state.filterOptions.dateTo)
                    const requestDate = new Date(request.request_date)
                    if (requestDate > toDate) return false
                }

                return true
            })
        },

        pendingRequests: (state) => {
            return state.requests.filter(r => ['requested', 'assigned'].includes(r.status))
        },
        completedRequests: (state) => {
            return state.requests.filter(r => r.status === 'closed')
        }
    },
    actions: {
        async fetchRequests(params = {}) {
            this.loading = true
            this.error = null

            if (this.filterOptions.status) {
                params.status = this.filterOptions.status
            }

            if (this.filterOptions.dateFrom) {
                params.date_from = this.filterOptions.dateFrom
            }

            if (this.filterOptions.dateTo) {
                params.date_to = this.filterOptions.dateTo
            }
            try {
                const response = await getServiceRequests(params)
                this.requests = response.data.service_requests
                return response.data.service_requests
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to fetch service requests'
                throw error
            } finally {
                this.loading = false
            }
        },
        async fetchRequestById(id) {
            this.loading = true
            this.error = null

            try {
                const response = await getServiceRequest(id)
                this.currentRequest = response.data.service_request
                return response.data.service_request
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to fetch service request'
                throw error
            } finally {
                this.loading = false
            }
        },

        async createNewRequest(requestData) {
            this.loading = true
            this.error = null

            try {
                const response = await createServiceRequest(requestData)
                this.requests.unshift(response.data.service_request)
                return response.data.service_request
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to create service request'
                throw error
            } finally {
                this.loading = false
            }
        },
        async updateExistingRequest(id, requestData) {
            this.loading = true
            this.error = null

            try {
                const response = await updateServiceRequest(id, requestData)

                const index = this.requests.findIndex(r => r.id === id)
                if (index !== -1) {
                    this.requests[index] = response.data.service_request
                }

                if (this.currentRequest && this.currentRequest.id === id) {
                    this.currentRequest = response.data.service_request
                }

                return response.data.service_request
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to update service request'
                throw error
            } finally {
                this.loading = false
            }
        },

        async cancelRequest(id) {
            this.loading = true
            this.error = null

            try {
                await cancelServiceRequest(id)

                const index = this.requests.findIndex(r => r.id === id)
                if (index !== -1) {
                    this.requests[index].status = 'cancelled'
                }

                if (this.currentRequest && this.currentRequest.id === id) {
                    this.currentRequest.status = 'cancelled'
                }

                return true
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to cancel service request'
                throw error
            } finally {
                this.loading = false
            }
        },
        async performRequestAction(id, action, reason = null) {
            this.loading = true
            this.error = null

            const actionData = { action }
            if (reason) actionData.reason = reason

            try {
                const response = await serviceRequestAction(id, actionData)

                const index = this.requests.findIndex(r => r.id === id)
                if (index !== -1) {
                    this.requests[index] = response.data.service_request
                }

                if (this.currentRequest && this.currentRequest.id === id) {
                    this.currentRequest = response.data.service_request
                }

                if (action === 'reject') {
                    this.availableRequests = this.availableRequests.filter(r => r.id !== id)
                }

                return response.data.service_request
            } catch (error) {
                this.error = error.response?.data?.message || `Failed to ${action} service request`
                throw error
            } finally {
                this.loading = false
            }
        },
        async fetchAvailableRequests() {
            this.loading = true
            this.error = null

            try {
                const response = await getAvailableRequests()
                this.availableRequests = response.data.service_requests
                return response.data.service_requests
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to fetch available requests'
                throw error
            } finally {
                this.loading = false
            }
        },
        async submitReview(reviewData) {
            this.loading = true
            this.error = null

            try {
                const response = await submitReview(reviewData)

                const requestIndex = this.requests.findIndex(r => r.id === reviewData.service_request_id)
                if (requestIndex !== -1) {
                    this.requests[requestIndex].reviews.push(response.data.review)
                }
                return response.data.review
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to submit review'
                throw error
            }
            finally {
                this.loading = false
            }
        },

        setFilterOptions(options) {
            this.filterOptions = { ...this.filterOptions, ...options }
        },

        clearFilters() {
            this.filterOptions = {
                status: null,
                dateFrom: null,
                dateTo: null
            }
        }
    }
})