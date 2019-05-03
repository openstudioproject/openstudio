import T from './types'

export const classesBookReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.CLASSES_SET_BOOKING_OPTIONS_LOADING:
            return {
                ...state,
                loading: action.loading,
            }
        case T.CLASSES_REQUEST_BOOKING_OPTIONS:
            return {
                ...state,
                loading: true,
                loaded: false,
                data: {}
            }
        case T.CLASSES_RECEIVE_BOOKING_OPTIONS:
            return {
                ...state,
                loading: false,
                loaded: true,
                data: action.data.options,
            }
        case T.CLASSES_REQUEST_CLASSES_CUSTOMER:
            return {
                ...state,
                classes_loading: true,
                checked_loaded: false,
                classes_error: false,
                classes_error_message: ""
            }
        case T.CLASSES_RECEIVE_CLASSES_CUSTOMER:
            console.log('classes customer receive')
            console.log(action.data)

            return {
                ...state,
                classes_loading: false,
                checked_loaded: true,
                classes_error: action.data.error,
                classes_error_message: action.data.message
            }
        default:
            return {
                ...state
            }
    }
}
