import T from './types'


export const listReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.REQUEST_CUSTOMERS:
            return {
                ...state,
                loading: true,
                loaded: false,
                loading: action.loading,
            }
        case T.RECEIVE_CUSTOMERS:
            return {
                ...state,
                loading: false,
                loaded: true,
                data: action.data
            }
        case T.SET_CREATE_CUSTOMER_STATUS:
            return {
                ...state,
                create_customer: action.status
            }
        case T.SET_UPDATE_CUSTOMER_STATUS:
            return {
                ...state,
                update_customer: action.status
            }
        case T.REQUEST_CREATE_CUSTOMER:
            return {
                ...state,
                creating_customer: true
            }

        case T.RECEIVE_CREATE_CUSTOMER:
            let new_customer = action.data

            return {
                ...state,
                creating_customer: false,
                data: {
                    ...state.data,
                    new_customer
                }
            }
        case T.REQUEST_UPDATE_CUSTOMER:
            return {
                ...state,
                updating_customer: true
            }

        case T.RECEIVE_UPDATE_CUSTOMER:
            let updated_customer = action.data

            return {
                ...state,
                updating_customer: false,
                data: {
                    ...state.data,
                    [action.data.id] : updated_customer
                }
            }
        case T.CLEAR_DISPLAY_CUSTOMER_ID:
            return {
                ...state,
                displayID: null,
            }
        case T.SET_DISPLAY_CUSTOMER_ID:
            return {
                ...state,
                displayID: action.id,
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
        case T.CLEAR_SEARCH_VALUE:
            return {
                ...state,
                search_value: "",
            }
        case T.SET_SEARCH_VALUE:
            return {
                ...state,
                search_value: action.value,
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


