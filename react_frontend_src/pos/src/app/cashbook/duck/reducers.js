import T from './types'


function isEmpty(obj) {
    for(var key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
}


export const cashbookReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.REQUEST_CASH_COUNTS:
            return {
                ...state,
                cash_counts_loading: true,
                cash_counts_loaded: false,
            }
        case T.RECEIVE_CASH_COUNTS:
            return {
                ...state,
                cash_counts_loading: false,
                cash_counts_loaded: true,
                cash_counts_data: action.data
            }
        case T.REQUEST_EXPENSES:
            return {
                ...state,
                expenses_loading: true,
                expenses_loaded: false,
            }
        case T.RECEIVE_EXPENSES:
            return {
                ...state,
                expenses_loading: false,
                expenses_loaded: true,
                expenses_data: action.data
            }
        default:
            return {
                ...state
            }
    }
}


