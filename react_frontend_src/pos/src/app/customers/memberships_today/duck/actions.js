import T from './types'

export const requestMembershipsToday = () =>
    ({
        type: T.REQUEST_CUSTOMER_MEMBERSHIPS_TODAY
    })

export const receiveMembershipsToday = (data) =>
    ({
        type: T.RECEIVE_CUSTOMER_MEMBERSHIPS_TODAY,
        data
    })

export const clearMembershipsToday = () =>
    ({
        type: T.CLEAR_CUSTOMER_MEMBERSHIPS_TODAY
    })