import T from './types'

export const requestClasscards = () =>
    ({
        type: T.REQUEST_CUSTOMER_CLASSCARDS
    })

export const receiveClasscards = (data) =>
    ({
        type: T.RECEIVE_CUSTOMER_CLASSCARDS,
        data
    })