import T from './types'

export const listReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.REQUEST_CUSTOMERS:
            return {
                loading: true,
                loaded: false,
                loading: action.loading,
            }
        case T.RECEIVE_CUSTOMERS:
            return {
                loading: false,
                loaded: true,
                data: action.data
            }
        case T.CLEAR_SEARCH_TIMEOUT:
            return {
                ...state,
                searchTimeout: clearTimeout(state.searchTimeout), 
            }
        case T.SET_SEARCH_TIMEOUT:
            return {
                ...state,
                searchTimeout: action.timeout,
            }
        case T.CLEAR_SEARCH_CUSTOMER_ID:
            return {
                ...state,
                searchID: null,
            }
        case T.SET_SEARCH_CUSTOMER_ID:
            return {
                ...state,
                searchID: action.id,
            }
        case T.CLEAR_SELECTED_CUSTOMER_ID:
            return {
                ...state,
                selectedID: null,
            }
        case T.SET_SELECTED_CUSTOMER_ID:
            return {
                ...state,
                selectedID: action.id,
            }
        default:
            return {
                ...state
            }
    }
}


