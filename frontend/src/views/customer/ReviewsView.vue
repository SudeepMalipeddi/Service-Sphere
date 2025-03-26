<template>
    <div class="customer-reviews-view">
        <h1>My Reviews</h1>

        <div class="card">
            <div class="card-body">
                <div v-if="loading" class="text-center my-5">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>

                <div v-else-if="reviews.length === 0" class="text-center my-5">
                    <p>You haven't submitted any reviews yet.</p>
                    <router-link to="/customer/requests" class="btn btn-primary">
                        View Service Requests
                    </router-link>
                </div>

                <div v-else>
                    <div class="list-group">
                        <div v-for="review in reviews" :key="review.id" class="list-group-item">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h5>{{ review.service_name }}</h5>
                                    <p class="mb-1"><strong>Professional:</strong> {{ review.professional_name }}</p>
                                    <p class="mb-1"><small class="text-muted">Submitted on {{
                                        formatDate(review.created_at) }}</small></p>
                                </div>
                                <div class="star-rating">
                                    <span v-for="i in 5" :key="i" :class="{ 'filled': review.rating >= i }">
                                        ★
                                    </span>
                                </div>
                            </div>

                            <p class="mt-2">{{ review.comment || 'No comment provided' }}</p>

                            <div class="d-flex gap-2 mt-2">
                                <button class="btn btn-sm btn-outline-primary" @click="openEditModal(review)">
                                    Edit Review
                                </button>
                                <button class="btn btn-sm btn-outline-danger" @click="confirmDeleteReview(review)">
                                    Delete Review
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Edit Review Modal -->
        <div v-if="showEditModal && currentReview" class="modal-overlay">
            <div class="modal-content">
                <h2>Edit Review</h2>
                <form @submit.prevent="updateReview">
                    <div class="mb-3">
                        <label class="form-label">Rating:</label>
                        <div class="numeric-rating">
                            <div v-for="i in 5" :key="i" :class="['rating-number', { 'active': editForm.rating >= i }]"
                                @click="editForm.rating = i">
                                {{ i }}
                            </div>
                        </div>
                        <small class="text-muted">Selected: {{ editForm.rating || 'None' }}/5</small>
                    </div>

                    <div class="mb-3">
                        <label class="form-label">Comment:</label>
                        <textarea class="form-control" v-model="editForm.comment" rows="3"
                            placeholder="Share your experience..."></textarea>
                    </div>

                    <div class="d-flex justify-content-between">
                        <button type="submit" class="btn btn-primary" :disabled="loading">
                            {{ loading ? 'Saving...' : 'Save Changes' }}
                        </button>
                        <button type="button" class="btn btn-secondary" @click="showEditModal = false">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Delete Confirmation Modal -->
        <div v-if="showDeleteModal && currentReview" class="modal-overlay">
            <div class="modal-content">
                <h2>Delete Review</h2>
                <p>Are you sure you want to delete your review for <strong>{{ currentReview.service_name }}</strong>?
                </p>
                <p>This action cannot be undone.</p>

                <div class="d-flex justify-content-between mt-4">
                    <button class="btn btn-danger" @click="deleteReview" :disabled="loading">
                        {{ loading ? 'Deleting...' : 'Delete Review' }}
                    </button>
                    <button class="btn btn-secondary" @click="showDeleteModal = false">
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { formatDate } from '@/utils/formatters';
import axios from 'axios';
import api from '@/api';

// State
const loading = ref(false);
const reviews = ref([]);
const showEditModal = ref(false);
const showDeleteModal = ref(false);
const currentReview = ref(null);
const editForm = ref({ rating: 0, comment: '' });

// Fetch the customer's reviews
const fetchReviews = async () => {
    loading.value = true;
    try {
        // Get the customer ID from localStorage
        const user = JSON.parse(localStorage.getItem('user'));

        // Fetch reviews for this customer
        const response = await axios.get('/reviews', {
            params: { customer_id: user.customer_id },
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });

        reviews.value = response.data.reviews;
    } catch (error) {
        console.error('Error fetching reviews:', error);
        const event = new CustomEvent('show-error', {
            detail: 'Failed to load reviews. Please try again later.'
        });
        window.dispatchEvent(event);
    } finally {
        loading.value = false;
    }
};

// Open the edit modal with the selected review
const openEditModal = (review) => {
    currentReview.value = review;
    editForm.value.rating = review.rating;
    editForm.value.comment = review.comment || '';
    showEditModal.value = true;
};

// Update a review
const updateReview = async () => {
    if (!currentReview.value || editForm.value.rating < 1) return;

    loading.value = true;
    try {
        const response = await axios.put(`/reviews/${currentReview.value.id}`, {
            rating: editForm.value.rating,
            comment: editForm.value.comment
        }, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('accessToken')}`
            }
        });

        // Update the review in the list
        const index = reviews.value.findIndex(r => r.id === currentReview.value.id);
        if (index !== -1) {
            reviews.value[index] = response.data.review;
        }

        // Close the modal
        showEditModal.value = false;

        // Show success message
        const event = new CustomEvent('show-success', {
            detail: 'Review updated successfully!'
        });
        window.dispatchEvent(event);
    } catch (error) {
        console.error('Error updating review:', error);
        const event = new CustomEvent('show-error', {
            detail: error.response?.data?.message || 'Failed to update review'
        });
        window.dispatchEvent(event);
    } finally {
        loading.value = false;
    }
};

// Confirm deletion of a review
const confirmDeleteReview = (review) => {
    currentReview.value = review;
    showDeleteModal.value = true;
};

// Delete a review
const deleteReview = async () => {
    if (!currentReview.value) return;

    loading.value = true;
    try {
        await api.delete(`/reviews/${currentReview.value.id}`);

        reviews.value = reviews.value.filter(r => r.id !== currentReview.value.id);

        // Close the modal
        showDeleteModal.value = false;

        // Show success message
        const event = new CustomEvent('show-success', {
            detail: 'Review deleted successfully!'
        });
        window.dispatchEvent(event);
    } catch (error) {
        console.error('Error deleting review:', error);
        const event = new CustomEvent('show-error', {
            detail: error.response?.data?.message || 'Failed to delete review'
        });
        window.dispatchEvent(event);
    } finally {
        loading.value = false;
    }
};

// Load reviews when component mounts
onMounted(() => {
    fetchReviews();
});
</script>

<style scoped>
.star-rating {
    display: inline-block;
}

.star-rating span {
    font-size: 24px;
    color: #ccc;
    padding: 0 2px;
}

.star-rating span.filled {
    color: #ffc107;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    max-width: 500px;
    width: 100%;
}

.numeric-rating {
    display: flex;
    gap: 10px;
    margin-bottom: 5px;
}

.rating-number {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 1px solid #ccc;
    cursor: pointer;
    font-weight: bold;
    transition: all 0.2s ease;
}

.rating-number:hover {
    background-color: #e9ecef;
    border-color: #6c757d;
}

.rating-number.active {
    background-color: #007bff;
    color: white;
    border-color: #007bff;
}
</style>