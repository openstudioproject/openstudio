import React from "react"
import { v4 } from "uuid"

import CartListItem from "./CartListItem"

const CartList = ({items, onClick=f=>f}) => 
    <div>
        {items.map((cart_item, i) => 
            <CartListItem key={"ci_" + v4()}
                          item={cart_item}
                          onClick={onClick} />
            // <AttendanceListItem key={"ai_" + v4()}
            //                     data={ai} />
        )}
    </div>


export default CartList