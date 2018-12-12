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
                ...state,
                loading: true,
                loaded: false,
                data: {}
            }
        case T.RECEIVE_PRODUCTS:
            return {
                ...state,
                loading: false,
                loaded: true,
                data: action.data.data,
            }
        case T.REQUEST_PRODUCT_CATEGORIES:
            return {
                ...state,
                categories_loading: true,
                categories_loaded: false
            }
        case T.RECEIVE_PRODUCT_CATEGORIES:
            return {
                ...state,
                categories: action.data.data,
                categories_loading: false,
                categories_loaded: true
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
        case T.CLEAR_PRODUCTS_SEARCH_VALUE:
            return {
                ...state,
                search_value: "",
            }
        case T.SET_PRODUCTS_SEARCH_VALUE:
            return {
                ...state,
                search_value: action.value.toLowerCase(),
            }
        case T.CLEAR_CATEGORY_FILTER_ID:
            return {
                ...state,
                category_filter_id: null
            }
        case T.SET_CATEGORY_FILTER_ID:
            return {
                ...state,
                category_filter_id: action.id
            }
        default:
            return {
                ...state
            }
    }
}
