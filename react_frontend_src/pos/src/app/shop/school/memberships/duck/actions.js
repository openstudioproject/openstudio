import T from './types'


export const requestShopSchoolMemberships = () =>
    ({
        type: T.SHOP_SCHOOL_REQUEST_MEMBERSHIPS
    })

export const receiveShopSchoolMemberships = (data) =>
    ({
        type: T.SHOP_SCHOOL_RECEIVE_MEMBERSHIPS,
        data
    })

export const setShopSchoolMembershipsLoaded = (loaded) =>
    ({
        type: T.SHOP_SCHOOL_SET_MEMBERSHIPS_LOADED,
        loaded
    })

export const setShopSchoolMembershipsLoading = (loading) =>
    ({
        type: T.SHOP_SCHOOL_SET_MEMBERSHIPS_LOADING,
        loading
    })
