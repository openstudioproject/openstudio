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
            let pm_progress = state.loading_progress + 33

            return {
                ...state,
                loading_progress: pm_progress,
                payment_methods: action.data.data
            }
        case T.REQUEST_USER:
            return {
                ...state,
            }
        case T.RECEIVE_USER:
            let u_progress = state.loading_progress + 34

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
            let s_progress = state.loading_progress + 33

            return {
                ...state,
                loading_progress: s_progress,
                settings: action.data
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
