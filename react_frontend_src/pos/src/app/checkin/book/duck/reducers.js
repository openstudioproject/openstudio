import T from './types'

export const checkinBookReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.CHECKIN_SET_BOOKING_OPTIONS_LOADING:
            return {
                ...state
                loading: action.loading,
            }
        case T.CHECKIN_REQUEST_BOOKING_OPTIONS:
            return {
                ...state,
                loading: true,
                loaded: false,
                data: {}
            }
        case T.CHECKIN_RECEIVE_BOOKING_OPTIONS:
            return {
                ...state,
                loading: false,
                loaded: true,
                data: action.data.options,
            }
        case T.CHECKIN_REQUEST_CLASS:
            return {
                ...state,
                checkin_loading: true,
                checked_loaded: false,
                checkin_error: false,
                checkin_error_message: ""
            }
        case T.CHECKIN_RECEIVE_CLASS:
            return {
                ...state,
                checkin_loading: false,
                checked_loaded: true,
                checkin_error: false,
                checkin_error_message: ""
            }
        default:
            return {
                ...state
            }
    }
}
