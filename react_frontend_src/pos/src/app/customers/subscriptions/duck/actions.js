import T from './types'

export const requestSubscriptions = () =>
    ({
        type: T.REQUEST_CUSTOMER_SUBSCRIPTIONS
    })

export const receiveSubscriptions = (data) =>
    ({
        type: T.RECEIVE_CUSTOMER_SUBSCRIPTIONS,
        data
    })