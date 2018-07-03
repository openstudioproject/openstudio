import T from './types'

const appReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.SET_LOADER_MESSAGE:
            return {
                ...state,
                message: action.message
            }
        case T.SET_LOADER_STATUS:
            return {
                ...state,
                status: action.status
            }
        default :
            return state
    }
}

export default appReducer
