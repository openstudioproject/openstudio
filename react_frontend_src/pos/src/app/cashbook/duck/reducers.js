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
        case T.REQUEST_SET_CASH_COUNT:
            return {
                ...state,
                set_cash_count: true
            }
        case T.RECEIVE_SET_CASH_COUNT:
            return {
                ...state,
                set_cash_count: false,
                cash_counts_data: action.data.cash_counts_data,
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
        case T.SET_EXPENSES_SELECTED_ID:
            return {
                ...state,
                expenses_selectedID: action.id
            }
        case T.CLEAR_EXPENSES_SELECTED_ID:
            return {
                ...state,
                expenses_selectedID: null
            }
        case T.REQUEST_CREATE_EXPENSE:
            return {
                ...state,
                expense_create: true,
            }
        case T.RECEIVE_CREATE_EXPENSE:
            let return_value = {
                ...state,
                expense_create: false,
                expense_create_error_data: action.data.result.errors,
            }
            
            if (action.data.error == false) {
                return_value['expenses_data'] = {
                    ...state.expenses_data,
                    [action.data.result.id]: action.data.expense_data
               }
            }
        case T.REQUEST_UPDATE_EXPENSE:
            return {
                ...state,
                expense_update: true,
            }
        case T.RECEIVE_CREATE_EXPENSE:
            return {
                ...state,
                expense_update: false
            }
            // let return_value = {
            //     ...state,
            //     expense_create: false,
            //     expense_create_error_data: action.data.result.errors,
            // }
            
            // if (action.data.error == false) {
            //     return_value['expenses_data'] = {
            //         ...state.expenses_data,
            //         [action.data.result.id]: action.data.expense_data
            //    }
            // }
            
            
            return return_value
        default:
            return {
                ...state
            }
    }
}


