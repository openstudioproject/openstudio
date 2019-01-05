import T from './types'


export const requestCheckinClassAttendance = () =>
    ({
        type: T.CHECKIN_REQUEST_CLASS_ATTENDANCE
    })

export const receiveCheckinClassAttendance = (data) =>
    ({
        type: T.CHECKIN_RECEIVE_CLASS_ATTENDANCE,
        data
    })

export const requestCheckinClassAttendanceUpdateStatus = (clattID) =>
    ({
        type: T.CHECKIN_CLASS_ATTENDANCE_REQUEST_UPDATE_STATUS,
        clattID
    })

export const receiveCheckinClassAttendanceUpdateStatus = (data) =>
    ({
        type: T.CHECKIN_CLASS_ATTENDANCE_RECEIVE_UPDATE_STATUS,
        data
    })

export const requestCheckinClassAttendanceDelete = (clattID) =>
    ({
        type: T.CHECKIN_CLASS_ATTENDANCE_REQUEST_DELETE,
        clattID
    })

export const receiveCheckinClassAttendanceDelete = (data) =>
    ({
        type: T.CHECKIN_CLASS_ATTENDANCE_RECEIVE_DELETE,
        data
    })

export const setCheckinClassAttendanceLoaded = (loaded) =>
    ({
        type: T.CHECKIN_SET_CLASS_ATTENDANCE_LOADED,
        loaded
    })

export const setCheckinClassAttendanceLoading = (loading) =>
    ({
        type: T.CHECKIN_SET_CLASS_ATTENDANCE_LOADING,
        loading
    })

export const setCheckinClassAttendanceSearchCustomerID = (search_id) =>
    ({
        type: T.CHECKIN_SET_CLASS_ATTENDANCE_SEARCH_CUSTOMER_ID,
        search_id,
    })

export const clearCheckinAttendanceSearchTimeout = () =>
    ({
        type: T.CHECKIN_ATTENDANCE_CLEAR_SEARCH_TIMEOUT
    })

export const setCheckinAttendanceSearchTimeout = (timeout) =>
    ({
        type: T.CHECKIN_ATTENDANCE_SET_SEARCH_TIMEOUT,
        timeout,
    })

export const clearCheckinAttendanceSearchValue = () =>
    ({
        type: T.CHECKIN_ATTENDANCE_CLEAR_SEARCH_VALUE
    })

export const setCheckinAttendanceSearchValue = (value) =>
    ({
        type: T.CHECKIN_ATTENDANCE_SET_SEARCH_VALUE,
        value
    })

export const clearCheckinAttendanceSearchCustomerID = () =>
    ({
        type: T.CHECKIN_ATTENDANCE_CLEAR_SEARCH_CUSTOMER_ID
    })

export const setCheckinAttendanceSearchCustomerID = (id) =>
    ({
        type: T.CHECKIN_ATTENDANCE_SET_SEARCH_CUSTOMER_ID,
        id
    })