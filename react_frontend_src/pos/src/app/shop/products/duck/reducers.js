import T from './types'

export const shopProductsReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.SET_PRODUCTS_LOADING:
            return {
                ...state,
                loading: action.loading,
            }
        case T.REQUEST_PRODUCTS:
            return {
                loading: true,
                loaded: false,
                data: {}
            }
        case T.RECEIVE_PRODUCTS:
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
