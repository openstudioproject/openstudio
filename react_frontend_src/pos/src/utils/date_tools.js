export function toISODate(date) {
    let month = date.getMonth() + 1
    return date.getFullYear() + '-' + month + '-' + date.getDate()
}

