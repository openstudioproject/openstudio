import T from './types'

export const checkinAttendanceReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.CHECKIN_SET_CLASS_ATTENDANCE_LOADING:
            return {
                ...state,
                loading: action.loading,
            }
        case T.CHECKIN_REQUEST_CLASS_ATTENDANCE:
            return {
                loading: true,
                loaded: false,
                data: {}
            }
        case T.CHECKIN_RECEIVE_CLASS_ATTENDANCE:
            return {
                loading: false,
                loaded: true,
                data: action.data.attendance,
            }
        case T.CHECKIN_SET_CLASS_ATTENDANCE_SEARCH_CUSTOMER_ID:
            return {
                ...state,
                search_customer_id: action.search_customer_id,
            }
        case T.CHECKIN_ATTENDANCE_CLEAR_SEARCH_TIMEOUT:
            return {
                ...state,
                searchTimeout: clearTimeout(state.searchTimeout),
                
            }
        case T.CHECKIN_ATTENDANCE_SET_SEARCH_TIMEOUT:
            return {
                ...state,
                searchTimeout: action.timeout,
            }
        case T.CHECKIN_ATTENDANCE_CLEAR_SEARCH_CUSTOMER_ID:
            return {
                ...state,
                searchCustomerID: null,
            }
        case T.CHECKIN_ATTENDANCE_SET_SEARCH_CUSTOMER_ID:
            return {
                ...state,
                searchCustomerID: action.id,
            }
        case T.CHECKIN_ATTENDANCE_CLEAR_SEARCH_VALUE:
            return {
                ...state,
                searchValue: "",
            }
        case T.CHECKIN_ATTENDANCE_SET_SEARCH_VALUE:
            return {
                ...state,
                searchValue: action.value.toLowerCase(),
            }
        default:
            return {
                ...state
            }
    }
}
