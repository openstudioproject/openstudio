import T from './types'

export const requestClasscards = () =>
    ({
        type: T.REQUEST_CUSTOMERS_CLASSCARDS
    })

export const receiveClasscards = (data) =>
    ({
        type: T.RECEIVE_CUSTOMERS_CLASSCARDS,
        data
    })