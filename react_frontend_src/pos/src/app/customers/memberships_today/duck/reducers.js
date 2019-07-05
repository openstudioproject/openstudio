import T from './types'

export const customersMembershipsTodayReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.CLEAR_CUSTOMER_MEMBERSHIPS_TODAY:
            return {
                ...state,
                loading: false,
                loaded: false,
                data: {}
            }
        case T.REQUEST_CUSTOMER_MEMBERSHIPS_TODAY:
            return {
                ...state,
                loading: true,
                loaded: false,
            }
        case T.RECEIVE_CUSTOMER_MEMBERSHIPS_TODAY:
            return {
                ...state,
                loading: false,
                loaded: true,
                data: action.data.data
            }
        default:
            return {
                ...state
            }
    }
}
