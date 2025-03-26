export function getToken() {
    return localStorage.getItem('accessToken');
}

export function isAuthenticated() {
    const token = localStorage.getItem('accessToken')

    if (!token) {
        return false
    }
}

export function getRefreshToken() {
    return localStorage.getItem('refreshToken')
}
export function getUserRole() {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return user.role || null
}

export function setAuth(data) {
    localStorage.setItem('accessToken', data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
    localStorage.setItem('user', JSON.stringify(data.user))
}

export function clearAuth() {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
}

export function getUser() {
    return JSON.parse(localStorage.getItem('user') || '{}')
}