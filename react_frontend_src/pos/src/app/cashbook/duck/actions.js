import T from './types'


export const requestCashCounts = () =>
    ({
        type: T.REQUEST_CASH_COUNTS
    })

export const receiveCashCounts = (data) =>
    ({
        type: T.RECEIVE_CASH_COUNTS,
        data
    })

export const requestExpenses = () =>
    ({
        type: T.REQUEST_EXPENSES
    })

export const receiveExpenses = (data) =>
    ({
        type: T.RECEIVE_EXPENSES,
        data
    })

// export const requestCreateCustomer = (data) =>
//     ({
//         type: T.REQUEST_CREATE_CUSTOMER,
//         data
//     })

// export const receiveCreateCustomer = (data) =>
//     ({
//         type: T.RECEIVE_CREATE_CUSTOMER,
//         data
//     })
