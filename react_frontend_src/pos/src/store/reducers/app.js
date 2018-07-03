import C from '../../constants'

export const loader = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case C.SET_LOADER_MESSAGE:
            return {
                ...state,
                message: action.message
            }
        case C.SET_LOADER_STATUS:
            return {
                ...state,
                status: action.status
            }
        default :
            return state
    }
}