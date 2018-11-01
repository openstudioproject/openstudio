import React from "react"
import { v4 } from "uuid"

import CartToolsCustomer from "./CartToolsCustomerContainer"


const CartTools = ({customers, deleteSelectedItem, cart_selected_item}) => 
    <div className="box box-solid">
        <div className="box-body">
            <div className="col-md-6">
                <CartToolsCustomer customers={customers} />
                Customer & Payment
            </div>
            <div className="col-md-6">
                {console.log('cart_selected_item')}
                {console.log(cart_selected_item)}
                <button className="btn btn-default btn-block"
                        disabled={(!cart_selected_item.length)}
                        onClick={ () => deleteSelectedItem() }>
                    Delete item
                </button>
            </div>
        </div>
    </div>


export default CartTools