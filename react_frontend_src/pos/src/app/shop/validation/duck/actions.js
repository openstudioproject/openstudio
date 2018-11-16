import T from './types'


export const setSelectedPaymentMethod = (data) =>
    ({
        type: T.SET_SELECTED_PAYMENT_METHOD,
        data
    })

