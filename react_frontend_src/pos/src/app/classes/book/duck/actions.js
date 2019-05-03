import T from './types'


export const requestClassesBookingOptions = () =>
    ({
        type: T.CLASSES_REQUEST_BOOKING_OPTIONS
    })

export const receiveClassesBookingOptions = (data) =>
    ({
        type: T.CLASSES_RECEIVE_BOOKING_OPTIONS,
        data
    })

export const setClassesBookingOptionsLoaded = (loaded) =>
    ({
        type: T.CLASSES_SET_BOOKING_OPTIONS_LOADED,
        loaded
    })

export const setClassesBookingOptionsLoading = (loading) =>
    ({
        type: T.CLASSES_SET_BOOKING_OPTIONS_LOADING,
        loading
    })

export const requestClassesCustomer = () =>
    ({
        type: T.CLASSES_REQUEST_CLASSES_CUSTOMER
    })

export const receiveClassesCustomer = (data) =>
    ({
        type: T.CLASSES_RECEIVE_CLASSES_CUSTOMER,
        data
    })
