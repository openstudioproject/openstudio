import T from './types'


export const requestClassesRevenue = () =>
    ({
        type: T.CLASSES_REQUEST_REVENUE
    })

export const receiveClassesRevenue = (data) =>
    ({
        type: T.CLASSES_RECEIVE_REVENUE,
        data
    })

export const requestClassesTeacherPayment = () =>
    ({ 
        type: T.CLASSES_REQUEST_TEACHER_PAYMENT
    })

export const receiveClassesTeacherPayment = (data) =>
    ({
        type: T.CLASSES_RECEIVE_TEACHER_PAYMENT,
        data
    })

export const requestClassesVerifyTeacherPayment = () =>
    ({ 
        type: T.CLASSES_REQUEST_VERIFY_TEACHER_PAYMENT
    })

export const receiveClassesVerifyTeacherPayment = (data) =>
    ({
        type: T.CLASSES_RECEIVE_VERIFY_TEACHER_PAYMENT,
        data
    })

export const setClassesRevenueLoaded = (loaded) =>
    ({
        type: T.CLASSES_SET_REVENUE_LOADED,
        loaded
    })

export const setClassesRevenueLoading = (loading) =>
    ({
        type: T.CLASSES_SET_REVENUE_LOADING,
        loading
    })
