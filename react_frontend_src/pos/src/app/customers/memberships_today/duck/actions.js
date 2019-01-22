import T from './types'

export const requestMembershipsToday = () =>
    ({
        type: T.REQUEST_CUSTOMERS_MEMBERSHIPS_TODAY
    })

export const receiveMembershipsToday = (data) =>
    ({
        type: T.RECEIVE_CUSTOMERS_MEMBERSHIPS_TODAY,
        data
    })