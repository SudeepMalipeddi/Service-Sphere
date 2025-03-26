import api from '.';


export function getCustomer(customerId) {
    return api.get(`/api/customers/${customerId}`);
}

export function updateCustomer(customerId, customerData) {
    return api.put(`/api/customers/${customerId}`, customerData);
}
