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

    