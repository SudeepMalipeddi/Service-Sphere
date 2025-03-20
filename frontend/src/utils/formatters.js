export function formatDate(dateString) {
    if (!dateString) return ''

    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    })
}


export function formatTime(dateString) {
    if (!dateString) return ''

    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    })
}

export function formatDateTime(dateString) {
    if (!dateString) return ''

    return `${formatDate(dateString)} at ${formatTime(dateString)}`
}

export function formatPrice(price) {
    return `₹${parseFloat(price).toFixed(2)}`
}

export function formatDuration(minutes) {
    if (!minutes) return ''

    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60

    if (hours > 0 && mins > 0) {
        return `${hours}h ${mins}m`
    } else if (hours > 0) {
        return `${hours}h`
    } else {
        return `${mins}m`
    }
}

export function capitalize(string) {
    if (!string) return ''
    return string.charAt(0).toUpperCase() + string.slice(1)
}


export function formatStatus(status) {
    if (!status) return ''


    return status.replace(/_/g, ' ').split(' ')
        .map(word => capitalize(word))
        .join(' ')
}

export function truncate(text, length = 100) {
    if (!text) return ''

    if (text.length <= length) return text

    return text.substring(0, length) + '...'
}