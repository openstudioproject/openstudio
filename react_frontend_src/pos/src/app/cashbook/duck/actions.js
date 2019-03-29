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

export const requestSetCashCount = () =>
    ({
        type: T.REQUEST_SET_CASH_COUNT
    })

export const receiveSetCashCount = (data) =>
    ({
        type: T.RECEIVE_SET_CASH_COUNT,
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

export const requestCreateExpense = () =>
    ({
        type: T.REQUEST_CREATE_EXPENSE
    })

export const receiveCreateExpense = (data) =>
    ({
        type: T.RECEIVE_CREATE_EXPENSE,
        data
    })
