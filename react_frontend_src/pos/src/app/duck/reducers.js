import { ENGLISH_TRANSLATION } from './messages/en'
import T from './types'

const initialState = {
    language: ENGLISH_TRANSLATION.language,
    messages: ENGLISH_TRANSLATION.messages
}

export const appReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.REQUEST_PAYMENT_METHODS:
            return {
                ...state,
            }
        case T.RECEIVE_PAYMENT_METHODS:
            let pm_progress = state.loading_progress + 20

            return {
                ...state,
                loading_progress: pm_progress,
                payment_methods: action.data.data
            }
        case T.REQUEST_PRODUCT_CATEGORIES:
            return {
                ...state,
                shop: {
                    ...state.shop,
                    products: {
                        ...state.shop.products,
                        product_categories_loading: true,
                        product_categories_loaded: false
                    }
                }
            }
        case T.RECEIVE_PRODUCT_CATEGORIES:
            let pm_progress = state.loading_progress + 20

            return {
                ...state,
                shop: {
                    ...state.shop,
                    products: {
                        ...state.shop.products,
                        product_categories: action.data.data,
                        product_categories_loading: false,
                        product_categories_loaded: true
                    }
                }
            }
        case T.REQUEST_USER:
            return {
                ...state,
            }
        case T.RECEIVE_USER:
            let u_progress = state.loading_progress + 20

            return {
                ...state,
                loading_progress: u_progress,
                user: action.data
            }
        case T.REQUEST_SETTINGS:
            return {
                ...state,
            }
        case T.RECEIVE_SETTINGS:
            let s_progress = state.loading_progress + 20

            return {
                ...state,
                loading_progress: s_progress,
                settings: action.data
            }
        case T.REQUEST_VALIDATE_CART:
            return {
                ...state,
                cart_validating: true,
                cart_validated: false
            }
        case T.RECEIVE_VALIDATE_CART:
            console.log('cart validation data:')
            console.log(action.data)

            return {
                ...state,
                cart_validating: false,
                cart_validated: true,
                cart_validation_error: action.data.error,
                cart_validation_data: action.data
            }
        case T.SET_ERROR:
            return {
                ...state,
                error: action.error
            }
        case T.SET_ERROR_MESSAGE:
            return {
                ...state,
                error_message: action.message
            }
        case T.SET_ERROR_DATA:
            return {
                ...state,
                error_data: action.data
            }
        case T.SET_LOADING_MESSAGE:
            return {
                ...state,
                loading_message: action.message
            }
        case T.SET_LOADING_PROGRESS:
            return {
                ...state,
                loading_progress: action.progress
            }
        case T.SET_LOADED:
            return {
                ...state,
                loaded: (state.loading_progress == 100) ? true : false
            }
        case T.SET_LOADING:
            return {
                ...state,
                loading:  (state.loading_progress == 100) ? false : true
            }
        case T.SET_PAGE_TITLE:
            return {
                ...state,
                current_page_title: action.title
            }
        default:
            return {
                ...state
            }
    }
}


export const localeReducer = (state = initialState, action={ type: null }) => {
    switch (action.type) {
        case T.SET_LOCALE:
        switch (action.locale) {
            case 'en':
                return {
                    ...state,
                    language: ENGLISH_TRANSLATION.lang,
                    messages: ENGLISH_TRANSLATION.messages
                }
            default:
                return {
                    ...state,
                    language: ENGLISH_TRANSLATION.lang,
                    messages: ENGLISH_TRANSLATION.messages
                }
        }
    default :
        return state
    }
}
