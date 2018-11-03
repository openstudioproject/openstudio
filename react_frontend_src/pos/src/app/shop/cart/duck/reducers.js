import T from './types'

export const shopCartReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.ADD_ITEM:
            //TODO Find item, if item already in items, increase qty; ELSE add item
            let item_exists = false
            let i = 0

            for (i = 0; i < state.items.length; i++) {
                let item = state.items[i]
                if ((item.product_type === action.data.product_type) && (item.data.id === action.data.data.id)) {
                    item_exists = true
                    break
                }
            }

            console.log(action.data)

            if (item_exists) {
                // increate quantity if product, don't do anything for school products
                if (action.data.item_type === 'product') {
                    return {
                        ...state,
                        items: state.items.map((item, index) =>
                            index === i ? {...item, quantity: item.quantity + 1} : item
                        )
                    }
                } else {
                    return {
                        ...state
                    }
                }
            } else {
                // add new item, don't increate quantity
                return {
                    ...state,
                    items: [...state.items, action.data]
                }
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
