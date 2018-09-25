import T from './Types'

export const requestMemberships = () =>
    ({
        type: T.REQUEST_CUSTOMER_MEMBERSHIPS
    })

export const receiveMemberships = (data) =>
    ({
        type: T.RECEIVE_CUSTOMER_MEMBERSHIPS,
        data
    })