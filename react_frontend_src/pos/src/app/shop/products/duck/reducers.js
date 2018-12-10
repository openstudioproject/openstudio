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
        case T.CLEAR_SEARCH_TIMEOUT:
            return {
                ...state,
                searchTimeout: clearTimeout(state.searchTimeout), 
            }
        case T.SET_SEARCH_TIMEOUT:
            return {
                ...state,
                searchTimeout: action.timeout,
            }
        case T.CLEAR_SEARCH_PRODUCT_ID:
            return {
                ...state,
                searchID: null,
            }
        case T.SET_SEARCH_PRODUCT_ID:
            return {
                ...state,
                searchID: action.id,
            }
        case T.CLEAR_SEARCH_VALUE:
            return {
                ...state,
                search_value: "",
            }
        case T.SET_SEARCH_VALUE:
            return {
                ...state,
                search_value: action.value.toLowerCase(),
            }
        default:
            return {
                ...state
            }
    }
}
