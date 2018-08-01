import T from './types'


export const requestCheckinRevenue = () =>
    ({
        type: T.CHECKIN_REQUEST_REVENUE
    })

export const receiveCheckinRevenue = (data) =>
    ({
        type: T.CHECKIN_RECEIVE_REVENUE,
        data
    })

export const requestCheckinTeacherPayment = () =>
    ({ 
        type: T.CHECKIN_REQUEST_TEACHER_PAYMENT
    })

export const receiveCheckinTeacherPayment = (data) =>
    ({
        type: T.CHECKIN_RECEIVE_TEACHER_PAYMENT,
        data
    })

export const requestCheckinVerifyTeacherPayment = () =>
    ({ 
        type: T.CHECKIN_REQUEST_VERIFY_TEACHER_PAYMENT
    })

export const receiveCheckinVerifyTeacherPayment = (data) =>
    ({
        type: T.CHECKIN_RECEIVE_VERIFY_TEACHER_PAYMENT,
        data
    })

export const setCheckinRevenueLoaded = (loaded) =>
    ({
        type: T.CHECKIN_SET_REVENUE_LOADED,
        loaded
    })

export const setCheckinRevenueLoading = (loading) =>
    ({
        type: T.CHECKIN_SET_REVENUE_LOADING,
        loading
    })
