import T from './types'


export const requestClassesClassAttendance = () =>
    ({
        type: T.CLASSES_REQUEST_CLASS_ATTENDANCE
    })

export const receiveClassesClassAttendance = (data) =>
    ({
        type: T.CLASSES_RECEIVE_CLASS_ATTENDANCE,
        data
    })

export const requestClassesClassAttendanceUpdateStatus = (clattID) =>
    ({
        type: T.CLASSES_CLASS_ATTENDANCE_REQUEST_UPDATE_STATUS,
        clattID
    })

export const receiveClassesClassAttendanceUpdateStatus = (data) =>
    ({
        type: T.CLASSES_CLASS_ATTENDANCE_RECEIVE_UPDATE_STATUS,
        data
    })

export const requestClassesClassAttendanceDelete = (clattID) =>
    ({
        type: T.CLASSES_CLASS_ATTENDANCE_REQUEST_DELETE,
        clattID
    })

export const receiveClassesClassAttendanceDelete = (data) =>
    ({
        type: T.CLASSES_CLASS_ATTENDANCE_RECEIVE_DELETE,
        data
    })

export const setClassesClassAttendanceLoaded = (loaded) =>
    ({
        type: T.CLASSES_SET_CLASS_ATTENDANCE_LOADED,
        loaded
    })

export const setClassesClassAttendanceLoading = (loading) =>
    ({
        type: T.CLASSES_SET_CLASS_ATTENDANCE_LOADING,
        loading
    })

export const setClassesClassAttendanceSearchCustomerID = (search_id) =>
    ({
        type: T.CLASSES_SET_CLASS_ATTENDANCE_SEARCH_CUSTOMER_ID,
        search_id,
    })

export const clearClassesAttendanceSearchTimeout = () =>
    ({
        type: T.CLASSES_ATTENDANCE_CLEAR_SEARCH_TIMEOUT
    })

export const setClassesAttendanceSearchTimeout = (timeout) =>
    ({
        type: T.CLASSES_ATTENDANCE_SET_SEARCH_TIMEOUT,
        timeout,
    })

export const clearClassesAttendanceSearchValue = () =>
    ({
        type: T.CLASSES_ATTENDANCE_CLEAR_SEARCH_VALUE
    })

export const setClassesAttendanceSearchValue = (value) =>
    ({
        type: T.CLASSES_ATTENDANCE_SET_SEARCH_VALUE,
        value
    })

export const clearClassesAttendanceSearchCustomerID = () =>
    ({
        type: T.CLASSES_ATTENDANCE_CLEAR_SEARCH_CUSTOMER_ID
    })

export const setClassesAttendanceSearchCustomerID = (id) =>
    ({
        type: T.CLASSES_ATTENDANCE_SET_SEARCH_CUSTOMER_ID,
        id
    })