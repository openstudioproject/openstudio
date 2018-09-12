import T from './types'

export const shopSchoolSubscriptionsReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.SHOP_SCHOOL_SET_SUBSCRIPTIONS_LOADING:
            return {
                ...state,
                loading: action.loading,
            }
        case T.SHOP_SCHOOL_REQUEST_SUBSCRIPTIONS:
            return {
                loading: true,
                loaded: false,
                data: {}
            }
        case T.SHOP_SCHOOL_RECEIVE_SUBSCRIPTIONS:
            return {
                loading: false,
                loaded: true,
                data: action.data.data,
            }
        default:
            return {
                ...state
            }
    }
}
