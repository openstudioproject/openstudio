import T from './types'

export const checkinClassesReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.CHECKIN_SET_CLASSES_LOADING:
            return {
                loading: action.loading,
                ...state
            }
        case T.CHECKIN_REQUEST_CLASSES:
            return {
                loading: true,
                loaded: false,
                data: {}
            }
        case T.CHECKIN_RECEIVE_CLASSES:
            return {
                loading: false,
                loaded: true,
                data: action.data.classes,
            }
        default:
            return {
                ...state
            }
    }
}
