export function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
}

export function isValidPassword(password) {
    return password && password.length >= 6
}

export function isRequired(value) {
    if (value === null || value === undefined) return false
    return value.toString().trim().length > 0
}


export function isValidPhone(phone) {
    const re = /^\d{10}$/
    return re.test(phone.replace(/\D/g, ''))
}

export function isValidPincode(pincode) {
    const re = /^\d{6}$/
    return re.test(pincode)
}



export function isValidNumber(value) {
    return !isNaN(parseFloat(value)) && isFinite(value)
}


export function isValidPrice(price) {
    return isValidNumber(price) && parseFloat(price) > 0
}