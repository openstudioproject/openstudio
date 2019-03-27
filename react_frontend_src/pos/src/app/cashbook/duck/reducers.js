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


