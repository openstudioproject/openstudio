import React from "react"
import { v4 } from "uuid"

import CartListItem from "./CartListItem"

const CartList = ({items, selected_item, onClick=f=>f}) => 
    <div>
        {console.log('cart list')}
        {console.log(selected_item)}
        {items.map((cart_item, i) => 
            <CartListItem key={"ci_" + v4()}
                          item={cart_item}
                          selected_item={selected_item}
                          onClick={onClick} />
            // <AttendanceListItem key={"ai_" + v4()}
            //                     data={ai} />
        )}
    </div>


export default CartList