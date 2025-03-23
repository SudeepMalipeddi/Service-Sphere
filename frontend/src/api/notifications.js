import api from ".";

export function getNotifications(params = {}) {
    return api.get('/notifications', { params })
}

export function markAsRead(id) {
    return api.put(`/notifications/${id}`, {})
}

export function markAllAsRead() {
    return api.put('/notifications')
}

export function deleteNotification(id) {
    return api.delete(`/notifications/${id}`)
}