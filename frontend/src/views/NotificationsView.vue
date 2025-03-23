<template>
    <div class="notifications-view">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>Notifications</h1>
            <button class="btn btn-outline-primary" @click="markAllAsRead"
                :disabled="loading || !notifications.length || !unreadCount">
                Mark All as Read
            </button>
        </div>

        <div class="card">
            <div class="card-body">
                <div v-if="loading" class="text-center my-5">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>

                <div v-else-if="!notifications.length" class="text-center my-5">
                    <p>You don't have any notifications yet.</p>
                </div>

                <div v-else>
                    <div class="list-group">
                        <div v-for="notification in sortedNotifications" :key="notification.id"
                            class="list-group-item list-group-item-action"
                            :class="{ 'bg-light': !notification.is_read }">

                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">
                                    <span v-if="!notification.is_read" class="badge bg-primary me-2">New</span>
                                    {{ getNotificationTitle(notification.type) }}
                                </h6>
                                <small>{{ formatDate(notification.created_at) }}</small>
                            </div>
                            <p class="mb-1">{{ notification.message }}</p>
                            <div class="d-flex justify-content-end">
                                <button v-if="!notification.is_read" class="btn btn-sm btn-outline-primary me-2"
                                    @click="markAsRead(notification.id)">
                                    Mark as Read
                                </button>
                                <button class="btn btn-sm btn-outline-danger"
                                    @click="deleteNotification(notification.id)">
                                    Delete
                                </button>

                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { formatDate } from '@/utils/formatters';
import { useNotificationsStore } from '@/stores/notifications';

const notificationStore = useNotificationsStore();
const { notifications, unreadCount, loading, sortedNotifications } = storeToRefs(notificationStore);

const markAsRead = async (id) => {
    try {
        await notificationStore.markNotificationAsRead(id);
    } catch (error) {
        console.error('Mark as read error:', error);
    }
};

const markAllAsRead = async () => {
    try {
        await notificationStore.markAllNotificationsAsRead();
    } catch (error) {
        console.error('Mark all as read error:', error);
    }
};

const deleteNotification = async (id) => {
    try {

        await notificationStore.removeNotification(id);
    } catch (error) {
        console.error('Delete notification error:', error);
    }
};

const getNotificationTitle = (type) => {
    const titles = {
        'request': 'Service Request',
        'approval': 'Account Approval',
        'reminder': 'Reminder',
        'verification': 'Account Verification',
        'account_status': 'Account Status',
        'request_accepted': 'Request Accepted',
        'request_rejected': 'Request Rejected',
        'request_completed': 'Request Completed',
        'request_closed': 'Request Closed',
        'new_review': 'New Review',
        'export': 'Export Ready',
        'report': 'Report Ready',
        'overdue': 'Overdue Request'
    };
    return titles[type] || 'Notification';
};

onMounted(() => {
    notificationStore.fetchNotifications();
});
</script>
