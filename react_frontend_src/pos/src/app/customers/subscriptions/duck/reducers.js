import T from './types'

export const customersSubscriptionsReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.REQUEST_CUSTOMER_SUBSCRIPTIONS:
            return {
                ...state,
                loading: true,
                loaded: false,
                loading: action.loading,
            }
        case T.RECEIVE_CUSTOMER_SUBSCRIPTIONS:
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
