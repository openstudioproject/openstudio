import React from "react"
import { v4 } from "uuid"

import CartListItem from "./CartListItem"
import CartListTotal from "./CartListTotal"

const CartList = ({items, selected_item, onClick=f=>f}) => 
    <div>
        {items.map((cart_item, i) => 
            <CartListItem key={"ci_" + v4()}
                          item={cart_item}
                          selected_item={selected_item}
                          onClick={onClick} />
        )}
        <CartListTotal items={items} />
        
    </div>


export default CartList