import api from ".";

export function getServices(params = {}) {
    return api.get('/services', { params })
}

export function getService(id) {
    return api.get(`/services/${id}`)
}

export function createService(serviceData) {
    return api.post('/services', serviceData)
}

export function updateService(id, serviceData) {
    return api.put(`/services/${id}`, serviceData)
}

export function deleteService(id) {
    return api.delete(`/services/${id}`)
}