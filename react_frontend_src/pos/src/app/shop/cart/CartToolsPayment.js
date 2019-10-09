import React from "react"
import { v4 } from "uuid"


import OS_API from "../../../utils/os_api"
import axios_os from '../../../utils/axios_os'

const PaymentDisabled = (cart_items, customers) => {
    console.log('PaymentDisabled here')
    console.log(customers)
    console.log(cart_items.length)
    if (cart_items.length === 0) {
        console.log('no items in cart')
        return true
    } else {
        console.log('we have items in cart')
        // If shop product type selected, a customer has to be set
        var i;
        var has_school_product = false
        for (i = 0; i < cart_items.length; i++) { 
            if ((cart_items[i].item_type !== 'product') && (cart_items[i].item_type !== 'custom')) {
                has_school_product = true
                break
            }
        }

        console.log('has school product')
        console.log(has_school_product)

        if ((has_school_product) && !(customers.selectedID)) {
            return true
        } else {
            return false
        }
    }
}

const Button = ({history, children, cart_items, customers}) =>
    <button className="btn btn-default btn-block"
    // TODO: Add logic to onClick to check if there's a subscritpion in the cart, if so check if payment info is known, yes -> continue, no-> enter else: continue
            onClick={() => {
                
                history.push('/shop/payment')

            }}
            disabled={PaymentDisabled(cart_items, customers)}>
        {console.log('cart items button')}
        {console.log(cart_items)}
        {console.log(cart_items.length)}
        {children}
    </button>

{/* Check for selected customer when one or more school products was selected.. otherwise disable. */}

const CartToolsPayment = ({customers, cart_items, history, intl}) =>
    // <div onClick={() => history.push('/shop/payment')}>
    <div>
        {console.log(customers)}
        {console.log('cart items')}
        {console.log(cart_items)}
        {
            <Button history={history}
                    cart_items={cart_items}
                    customers={customers}
                    // selected={customers.list.selectedID}
            >
                <div className="text-center">
                    <i className="fa fa-chevron-circle-right fa-5x"></i> {' '} <br />
                    Payment

                </div>
                    {/* {
                        (customers.selectedID) ? 
                        customers.data[customers.selectedID].display_name : 'Customer'
                    } */}
            </Button>
        }
    </div>


export default CartToolsPayment