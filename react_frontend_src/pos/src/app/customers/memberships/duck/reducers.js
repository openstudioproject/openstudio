import T from './types'

export const customersMembershipsReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.REQUEST_CUSTOMER_MEMBERSHIPS:
            return {
                ...state,
                loading: true,
                loaded: false,
                loading: action.loading,
            }
        case T.RECEIVE_CUSTOMER_MEMBERSHIPS:
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
