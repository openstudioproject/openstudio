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

        

        // case T.CHECKIN_RECEIVE_CLASS_ATTENDANCE:
        //     return {
        //         loading: false,
        //         loaded: true,
        //         data: action.data.attendance,
        //     }
        // case T.CHECKIN_SET_CLASS_ATTENDANCE_SEARCH_CUSTOMER_ID:
        //     return {
        //         ...state,
        //         search_customer_id: action.search_customer_id,
        //     }
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
        case T.SET_SEARCH_CUSTOMER_ID:
            return {
                ...state,
                searchID: action.id,
            }
        default:
            return {
                ...state
            }
    }
}


