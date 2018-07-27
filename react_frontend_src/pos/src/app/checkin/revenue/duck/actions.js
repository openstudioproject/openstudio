import T from './types'


export const requestCheckinRevenue= () =>
    ({
        type: T.CHECKIN_REQUEST_REVENUE
    })

export const receiveCheckinRevenue= (data) =>
    ({
        type: T.CHECKIN_RECEIVE_REVENUE,
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
