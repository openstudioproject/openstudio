import T from './types'

export const customersSchoolInfoReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.CLEAR_CUSTOMER_SCHOOL_INFO:
            return {
                ...state,
                loading: false,
                loaded: false,
                data: {}
            }
        case T.REQUEST_CUSTOMER_SCHOOL_INFO:
            return {
                ...state,
                loading: true,
                loaded: false,
                data: {}
            }
        case T.RECEIVE_CUSTOMER_SCHOOL_INFO:
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
