import React from "react"
import { v4 } from "uuid"

import CartListItem from "./CartListItem"
import CartListTotal from "./CartListTotal"

const CartList = ({classes, items, selected_item, total, onClick=f=>f}) => 
    <div>
        {items.map((cart_item, i) => 
            <CartListItem key={"ci_" + v4()}
                          classes={classes}
                          item={cart_item}
                          selected_item={selected_item}
                          onClick={onClick} />
        )}
        <CartListTotal total={total} />
        
    </div>


export default CartList