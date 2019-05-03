import T from './types'

export const classesClassesReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.CLASSES_SET_CLASSES_LOADING:
            return {
                loading: action.loading,
                ...state
            }
        case T.CLASSES_REQUEST_CLASSES:
            return {
                loading: true,
                loaded: false,
                data: {}
            }
        case T.CLASSES_RECEIVE_CLASSES:
            return {
                loading: false,
                loaded: true,
                data: action.data.classes,
            }
        default:
            return {
                ...state
            }
    }
}
