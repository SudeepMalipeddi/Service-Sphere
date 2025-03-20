import api from ".";

export function getDashboardStats() {
    return api.get('/admin/dashboard')
}

export function getAdminProfessionals(params = {}) {
    return api.get('/admin/professionals', { params })
}

export function updateProfessionalStatus(data) {
    return api.put('/admin/professionals', data)
}

export function getAdminCustomers(params = {}) {
    return api.get('/admin/customers', { params })
}

export function updateCustomerStatus(data) {
    return api.put('/admin/customers', data)
}