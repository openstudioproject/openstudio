import React from "react"
import { v4 } from "uuid"

import CartToolsCustomer from "./CartToolsCustomerContainer"


const CartTools = ({customers}) => 
    <div className="box box-solid">
        <div className="box-body">
            <div className="col-md-4">
                <CartToolsCustomer customers={customers} />
                Customer & Payment
            </div>
            <div className="col-md-4">
                Numpad
            </div>
        </div>
    </div>


export default CartTools