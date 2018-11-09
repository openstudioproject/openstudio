import T from './types'


export const setSelectedPaymentMethod = (data) =>
    ({
        type: T.SET_SELECTED_PAYMENT_METHOD,
        data
    })


export const clearSelectedPaymentMethod = () =>
    ({
        type: T.CLEAR_SELECTED_PAYMENT_METHOD,
    })

