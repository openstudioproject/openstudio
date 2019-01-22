import T from './types'

export const requestSubscriptions = () =>
    ({
        type: T.REQUEST_CUSTOMERS_SUBSCRIPTIONS
    })

export const receiveSubscriptions = (data) =>
    ({
        type: T.RECEIVE_CUSTOMERS_SUBSCRIPTIONS,
        data
    })