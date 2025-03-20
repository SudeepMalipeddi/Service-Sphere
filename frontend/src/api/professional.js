import api from "."


export function verifyProfessional(id, verificationData) {
    return api.post(`/professionals/${id}/verify`, verificationData)
}

export function getProfessional(id) {
    return api.get(`/professionals/${id}`)
}

export function getProfessionals(params = {}) {
    return api.get('/professionals', { params })
}

export function updateProfessionalProfile(id, profileData) {
    return api.put(`/professionals/${id}`, profileData)
}

export function uploadDocuments(id, formData) {
    return api.put(`/professionals/${id}/verify`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}