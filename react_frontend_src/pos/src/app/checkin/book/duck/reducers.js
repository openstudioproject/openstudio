import T from './types'

export const checkinBookReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.CHECKIN_SET_BOOKING_OPTIONS_LOADING:
            return {
                loading: action.loading,
                ...state
            }
        case T.CHECKIN_REQUEST_BOOKING_OPTIONS:
            return {
                loading: true,
                loaded: false,
                data: {}
            }
        case T.CHECKIN_RECEIVE_BOOKING_OPTIONS:
            return {
                loading: false,
                loaded: true,
                data: action.data.attendance,
            }
        default:
            return {
                ...state
            }
    }
}
