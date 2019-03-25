import T from './types'


function isEmpty(obj) {
    for(var key in obj) {
        if(obj.hasOwnProperty(key))
            return false;
    }
    return true;
}


export const expensesReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.REQUEST_EXPENSES:
            return {
                ...state,
                loading: true,
                loaded: false,
            }
        case T.RECEIVE_EXPENSES:
            return {
                ...state,
                loading: false,
                loaded: true,
                data: action.data
            }
        default:
            return {
                ...state
            }
    }
}


