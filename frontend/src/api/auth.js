import api from ".";


export function login(credentials) {
    return api.post('/login', credentials);
}

export function register(userData) {
    return api.post('/register', userData);
}

export function refreshToken(refreshToken) {
    return api.post('/refresh', { refresh_token: refreshToken })
}

