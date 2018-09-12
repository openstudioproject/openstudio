import T from './types'


export const requestShopSchoolSubscriptions = () =>
    ({
        type: T.SHOP_SCHOOL_REQUEST_SUBSCRIPTIONS
    })

export const receiveShopSchoolSubscriptions = (data) =>
    ({
        type: T.SHOP_SCHOOL_RECEIVE_SUBSCRIPTIONS,
        data
    })

export const setShopSchoolSubscriptionsLoaded = (loaded) =>
    ({
        type: T.SHOP_SCHOOL_SET_SUBSCRIPTIONS_LOADED,
        loaded
    })

export const setShopSchoolSubscriptionsLoading = (loading) =>
    ({
        type: T.SHOP_SCHOOL_SET_SUBSCRIPTIONS_LOADING,
        loading
    })
