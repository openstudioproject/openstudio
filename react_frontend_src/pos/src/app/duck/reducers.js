import { ENGLISH_TRANSLATION } from './messages/en'
import T from './types'

const initialState = {
    language: ENGLISH_TRANSLATION.language,
    messages: ENGLISH_TRANSLATION.messages
}

export const appReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
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
                loaded: action.loaded
            }
        case T.SET_LOADING:
            return {
                ...state,
                loading: action.loading
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


export const userReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.REQUEST_USER:
            return {
                ...state,
                loading: true,
                loaded: false
            }
        case T.RECEIVE_USER:
            return {
                ...state,
                loading: false,
                loaded: true,
                data: action.data,
            }
        default:
            return {
                ...state
            }
    }
}
