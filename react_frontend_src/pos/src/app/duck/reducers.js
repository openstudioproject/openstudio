import T from './types'

const appReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.SET_LOADING_MESSAGE:
            return {
                ...state,
                loading_message: action.message
            }
        case T.SET_LOADING:
            return {
                ...state,
                loading: action.loading
            }
        default :
            return state
    }
}

export default appReducer
