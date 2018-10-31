import T from './types'

export const shopCartReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.ADD_ITEM:
            //TODO Find item, if item already in items, increase qty; ELSE add item


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
