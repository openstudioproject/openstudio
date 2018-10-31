import T from './types'

export const shopCartReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.ADD_ITEM:
            return {
                ...state,
                items: [...state.items, action.data]
            }
        default:
            return {
                ...state
            }
    }
}
