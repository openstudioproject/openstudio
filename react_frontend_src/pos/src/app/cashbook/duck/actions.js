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

export const setExpensesSelectedID = (id) =>
    ({
        type: T.SET_EXPENSES_SELECTED_ID,
        id
    })

export const clearExpensesSelectedID = () =>
    ({
        type: T.CLEAR_EXPENSES_SELECTED_ID,
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

export const requestUpdateExpense = () =>
    ({
        type: T.REQUEST_UPDATE_EXPENSE
    })

export const receiveUpdateExpense = (data) =>
    ({
        type: T.RECEIVE_UPDATE_EXPENSE,
        data
    })
