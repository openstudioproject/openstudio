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

export function python_dateformat_to_input_mask(py_dateformat) {
    switch (py_dateformat) {
        case "%d-%m-%Y":
            return "DD-MM-YYYY"
            break
        case "%m-%d-%Y":
            return "MM-DD-YYYY"
            break
        default:
            return "YYYY-MM-DD"
    }
}