import React from "react"
import { v4 } from "uuid"

import CartListItem from "./CartListItem"

const CartList = ({items}) => 
    <div className="box box-solid"> 
        <div className="box-body">
            {items.map((cart_item, i) => 
                console.log(cart_item)
                // <AttendanceListItem key={"ai_" + v4()}
                //                     data={ai} />
            )}
        </div>
    </div>


export default CartList