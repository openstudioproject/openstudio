import T from './types'


export const requestProducts = () =>
    ({
        type: T.REQUEST_PRODUCTS
    })

export const receiveProducts = (data) =>
    ({
        type: T.RECEIVE_PRODUCTS,
        data
    })
