import React from "react"
import { v4 } from "uuid"

import CartToolsCustomer from "./CartToolsCustomerContainer"


const CartTools = ({customers, deleteSelectedItem}) => 
    <div className="box box-solid">
        <div className="box-body">
            <div className="col-md-4">
                <CartToolsCustomer customers={customers} />
                Customer & Payment
            </div>
            <div className="col-md-4">
                <button onClick={() => deleteSelectedItem()}>
                    Delete
                </button>
            </div>
        </div>
    </div>


export default CartTools