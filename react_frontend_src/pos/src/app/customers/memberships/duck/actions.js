import T from './types'


export const requestMemberships = () =>
    ({
        type: T.REQUEST_MEMBERSHIPS
    })

export const receiveMemberships = (data) =>
    ({
        type: T.RECEIVE_MEMBERSHIPS,
        data
    })
