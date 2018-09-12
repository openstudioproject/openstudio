import T from './types'


export const requestShopSchoolClasscards = () =>
    ({
        type: T.SHOP_SCHOOL_REQUEST_CLASSCARDS
    })

export const receiveShopSchoolClasscards = (data) =>
    ({
        type: T.SHOP_SCHOOL_RECEIVE_CLASSCARDS,
        data
    })

export const setShopSchoolClasscardsLoaded = (loaded) =>
    ({
        type: T.SHOP_SCHOOL_SET_CLASSCARDS_LOADED,
        loaded
    })

export const setShopSchoolClasscardsLoading = (loading) =>
    ({
        type: T.SHOP_SCHOOL_SET_CLASSCARDS_LOADING,
        loading
    })
