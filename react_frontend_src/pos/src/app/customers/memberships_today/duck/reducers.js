import T from './types'

export const customersMembershipsTodayReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.REQUEST_CUSTOMERS_MEMBERSHIPS_TODAY:
            return {
                ...state,
                loading: true,
                loaded: false,
                loading: action.loading,
            }
        case T.RECEIVE_CUSTOMERS_MEMBERSHIPS_TODAY:
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
