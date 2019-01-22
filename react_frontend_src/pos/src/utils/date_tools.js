export function toISODate(date) {
    let month = date.getMonth() + 1
    return date.getFullYear() + '-' + month + '-' + date.getDate()
}

export function isoDateStringToDateObject(date_string) {
    return new Date(date_string)
}

export function formatDate(date) {
    var monthNames = [
      "January", "February", "March",
      "April", "May", "June", "July",
      "August", "September", "October",
      "November", "December"
    ]
  
    var day = date.getDate()
    var monthIndex = date.getMonth()
    var year = date.getFullYear()
  
    return monthNames[monthIndex] + ' ' + day + ', ' + year
}
