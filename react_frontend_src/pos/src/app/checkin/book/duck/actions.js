import T from './types'


export const requestCheckinBookingOptions = () =>
    ({
        type: T.CHECKIN_REQUEST_BOOKING_OPTIONS
    })

export const receiveCheckinBookingOptions = (data) =>
    ({
        type: T.CHECKIN_RECEIVE_BOOKING_OPTIONS,
        data
    })

export const setCheckinBookingOptionsLoaded = (loaded) =>
    ({
        type: T.CHECKIN_SET_BOOKING_OPTIONS_LOADED,
        loaded
    })

export const setCheckinBookingOptionsLoading = (loading) =>
    ({
        type: T.CHECKIN_SET_BOOKING_OPTIONS_LOADING,
        loading
    })

    