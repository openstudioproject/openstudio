import T from './types'

const calculateCartTotal = (items) => {
    let total = 0
    items.map((item, i) => {
        if (item.item_type == 'product') {
            if (item.data.price) {
                total = total + (item.data.price * item.quantity)
            }
        } else {
            if (item.data.Price) {
                total = total + (item.data.Price * item.quantity)
            }
        }
    })

    return total
}


export const shopCartReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.ADD_ITEM:
            //TODO Find item, if item already in items, increase qty; ELSE add item
            let new_items
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
                    new_items = state.items.map((item, index) =>
                        index === i ? {...item, quantity: item.quantity + 1} : item
                    )

                    return {
                        ...state,
                        total: calculateCartTotal(new_items),
                        items: new_items
                    }
                } else {
                    return {
                        ...state
                    }
                }
            } else {
                // add new item, don't increate quantity
                new_items = [...state.items, action.data]

                return {
                    ...state,
                    total: calculateCartTotal(new_items),
                    items: new_items
                }
            }
        case T.DELETE_SELECTED_ITEM:
            new_items = state.items.filter(item => item.id !== state.selected_item)

            return {
                ...state,
                selected_item: "",
                total: calculateCartTotal(state.items),
                items: new_items
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
