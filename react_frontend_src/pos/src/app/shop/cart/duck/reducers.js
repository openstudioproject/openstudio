import T from './types'

const calculateCartTotal = (items) => {
    let total = 0
    items.map((item, i) => {
        console.log(item)
        if ((item.item_type == 'product') || (item.item_type == 'custom') || (item.item_type == 'class_reconcile_later')) {
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
            let cart_item_index = 0

            // console.log('DEBUG ADD ITEM BEGIN')
            // console.log(action.data)

            for (cart_item_index = 0; cart_item_index < state.items.length; cart_item_index++) {
                let item = state.items[cart_item_index]
                // console.log(item)

                if ((item.item_type === action.data.item_type) 
                    && (item.data.id === action.data.data.id)
                    && (item.item_type != "class_dropin")) {
                    console.log('found match')
                    console.log(item.item_type)
                    console.log(action.data.item_type)
                    console.log(item.data.id)
                    console.log(action.data.data.id)
                    item_exists = true
                    break
                }
            }

            
            // console.log('item_exists')
            // console.log(item_exists)
            
            if (item_exists) {
                // increate quantity if product, don't do anything for school products
                if (action.data.item_type === 'product') {
                    new_items = state.items.map((item, index) =>
                        (index === cart_item_index) ? {...item, quantity: item.quantity + 1} : item
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
                total: calculateCartTotal(new_items),
                items: new_items
            }
        case T.SET_SELECTED_ITEM:
            return {
                ...state,
                selected_item: action.data
            }
        case T.CLEAR_ITEMS:
            return {
                ...state,
                selected_item: "",
                items: [],
                total: 0
            }
        default:
            return {
                ...state
            }
    }
}
