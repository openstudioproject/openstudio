import T from './types'

export const shopCartReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.ADD_ITEM:
            //TODO Find item, if item already in items, increase qty; ELSE add item
            let item_exists

            state.items.map((item) =>
                ((item.product_type == action.data.product_type) && (item.data.id == action.data.data.id)) ?
                    item_exists = true : item_exists = false
            )

            console.log('item_exists')
            console.log(item_exists)


            return {
                ...state,
                items: [...state.items, action.data]
            }
        case T.DELETE_SELECTED_ITEM:
            return {
                ...state,
                selected_item: "",
                items: state.items.filter(item => item.id !== state.selected_item)
            }
        case T.SET_SELECTED_ITEM:
            return {
                ...state,
                selected_item: action.data
            }
        default:
            return {
                ...state
            }
    }
}
