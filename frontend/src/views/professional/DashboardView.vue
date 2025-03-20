<!-- <template>
    <div>
        <h1>Dashboard View of Professional</h1>
    </div>
    <div v-if="isProfilePending" role="alert">
        <strong>Your profile is pending verification.</strong>
        <div v-if="profile.documents_url.length === 0">
            <p>Verification documents are required for approval.</p>
            <p>Please upload your verification documents to get approved.</p>
            <button @click="$router.push('/professional/profile')">
                Upload Documents
            </button>
        </div>
    </div>

    <div v-if="isProfileRejected" role="alert">
        <strong>Your profile verification was rejected.</strong>
        <p>Reason: {{ profile?.verification_reason || 'No reason provided' }}</p>
    </div>

    <div>
        <h2>Quick Actions</h2>
        <button @click="$router.push('/professional/requests')">My Service Requests</button>
        <button @click="$router.push('/professional/profile')">My Profile</button>
    </div>

</template>

<script setup>

import { getProfessional } from '@/api/professional';
import { getUser } from '@/utils/authutils';
import { ref, computed, onMounted } from 'vue';

const profile = ref(null);


const isProfilePending = computed(() => profile.value?.verification_status === 'pending');
const isProfileRejected = computed(() => profile.value?.verification_status === 'rejected');


computed(() => {
    
})

onMounted(async () => {
    try {
        const user = await getUser();

        if (user.id && user.role === 'professional') {
            const professionalId = user.professional_id;
            if (professionalId) {
                const response = await getProfessional(professionalId)
                profile.value = response.data.professional;

            }
        }
    } catch (err) {
        console.error("Failed to fetch profile:", err);
    }
})

</script> -->

<template>
    <div>
        <h1>Dashboard View of Professional</h1>

        <div v-if="profile">
            <div v-if="isProfilePending" role="alert">
                <strong>Your profile is pending verification.</strong>
                <div v-if="!profile.documents_url || profile.documents_url.length === 0">
                    <p>Verification documents are required for approval.</p>
                    <p>Please upload your verification documents to get approved.</p>
                    <button @click="$router.push('/professional/profile')">
                        Upload Documents
                    </button>
                </div>
            </div>

            <div v-if="isProfileRejected" role="alert">
                <!-- Retrieve the reason from notifications section afterwards -->
                <strong>Your profile verification was rejected.</strong>
                <!-- <p>Reason: {{ profile.verification_reason || 'No reason provided' }}</p> -->
            </div>

            <div>
                <h2>Quick Actions</h2>
                <button @click="$router.push('/professional/requests')">My Service Requests</button>
                <button @click="$router.push('/professional/profile')">My Profile</button>
            </div>
        </div>

        <div v-else>
            <p>Loading profile...</p>
        </div>
    </div>
</template>

<script setup>
import { getProfessional } from '@/api/professional';
import { useAuthStore } from '@/stores/auth';
import { getUser } from '@/utils/authutils';
import { ref, computed, onMounted } from 'vue';

const profile = ref(null);

const isProfilePending = computed(() => profile.value?.verification_status === 'pending');
const isProfileRejected = computed(() => profile.value?.verification_status === 'rejected');



onMounted(async () => {
    try {
        const user = await getUser();
        if (user?.id && user.role === 'professional') {
            const userId = user.id;
            const professionalId = getUser().professional_id;

            if (professionalId) {
                const response = await getProfessional(professionalId);
                profile.value = response.data.professional;
                console.log("Profile data:", profile.value);
            }
        }
    } catch (err) {
        console.error("Failed to fetch profile:", err);
    }
});
</script>
