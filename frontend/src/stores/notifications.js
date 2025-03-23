import { defineStore } from "pinia";
import { getNotifications, markAllAsRead, markAsRead, deleteNotification } from "@/api/notifications";


export const useNotificationsStore = defineStore("notifications", {
    state: () => ({
        notifications: [],
        loading: false,
        error: null,
        unreadCount: 0
    }),
    getters: {
        unreadNotifications: (state) => {
            return state.notifications.filter(n => !n.is_read)
        },

        sortedNotifications: (state) => {
            return [...state.notifications].sort((a, b) => {
                return new Date(b.created_at) - new Date(a.created_at)
            })
        }
    },
    actions: {
        async fetchNotifications(params = {}) {
            this.loading = true
            this.error = null

            try {
                const response = await getNotifications(params)
                this.notifications = response.data.notifications
                this.unreadCount = response.data.unread_count
                return response.data.notifications
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to fetch notifications'
                throw error
            } finally {
                this.loading = false
            }
        },
        async markNotificationAsRead(id) {
            this.loading = true
            this.error = null
            try {
                const response = await markAsRead(id)
                const index = this.notifications.findIndex(n => n.id === id)
                if (index !== -1) {
                    this.notifications[index].is_read = true
                }

                this.unreadCount = Math.max(0, this.unreadCount - 1)

                return response.data.notification
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to mark notification as read'
                throw error
            } finally {
                this.loading = false
            }
        },

        async markAllNotificationsAsRead() {
            this.loading = true
            this.error = null
            try {
                const response = await markAllAsRead()

                if (response.status === 200) {
                    this.notifications.forEach(n => {
                        n.is_read = true
                    })

                    this.unreadCount = 0
                    return true
                }
                else {
                    throw new Error('Failed to mark all notifications as read')
                }
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to mark all notifications as read'
                throw error
            } finally {
                this.loading = false
            }
        },

        async removeNotification(id) {
            this.loading = true
            this.error = null
            try {
                const response = await deleteNotification(id);

                if (response.status === 200) {
                    const notification = this.notifications.find(n => n.id === id)
                    const wasUnread = notification && !notification.is_read

                    // Remove from notifications array
                    this.notifications = this.notifications.filter(n => n.id !== id)

                    // Update unread count if it was unread
                    if (wasUnread) {
                        this.unreadCount = Math.max(0, this.unreadCount - 1)
                    }

                    return true
                }
                else {
                    throw new Error('Failed to delete notification')
                }
            } catch (error) {
                this.error = error.response?.data?.message || 'Failed to delete notification'
                throw error
            } finally {
                this.loading = false
            }
        }
    }

})