import api from ".";

export function getServiceRequests(params = {}) {
    return api.get('/service-requests', { params })
}

export function getServiceRequest(id) {
    return api.get(`/service-requests/${id}`)
}

export function createServiceRequest(requestData) {
    return api.post('/service-requests', requestData)
}

export function updateServiceRequest(id, requestData) {
    return api.put(`/service-requests/${id}`, requestData)
}

export function cancelServiceRequest(id) {
    return api.delete(`/service-requests/${id}`)
}

export function serviceRequestAction(id, actionData) {
    return api.post(`/service-requests/${id}/action`, actionData)
}

export function getAvailableRequests() {
    return api.get('/service-requests', { params: { available: true } })
}

export function submitReview(reviewData) {
    return api.post('/reviews', reviewData)
}

export function updateReview(reviewId, reviewData) {
    return api.put(`/reviews/${reviewId}`, reviewData)
}

export function getRequestReviews(requestId) {
    return api.get('/reviews', {
        params: { service_request_id: requestId }
    })
}