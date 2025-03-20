<template>
    <div>
        <h2>Verification Documents</h2>

        <div v-if="profile.documents_url && profile.documents_url.length > 0">
            <p>Uploaded Documents:</p>
            <ul>
                <li v-for="(doc, index) in profile.documents_url" :key="index">
                    <a :href="doc" target="_blank">View Document {{ index + 1 }}</a>
                </li>
            </ul>
        </div>

        <div v-else>
            <p>No documents uploaded yet.</p>
        </div>

        <div>
            <h3>Upload Verification Document</h3>
            <p>Please upload ID proof, certification, or experience documents.</p>

            <form @submit.prevent="uploadDocument">
                <div>
                    <label for="document">Select Document:</label>
                    <input type="file" id="document" @change="handleFileSelect" accept=".pdf,.jpg,.jpeg,.png" required>
                </div>

                <button type="submit" :disabled="uploading">
                    {{ uploading ? 'Uploading...' : 'Upload Document' }}
                </button>
            </form>
        </div>
    </div>
</template>

<script setup>
</script>