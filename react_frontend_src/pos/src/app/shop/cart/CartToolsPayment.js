import React from "react"
import { v4 } from "uuid"


const PaymentEnabled = (cart_items, customers) => {
    console.log(cart_items.length)
    if (cart_items.length === 0) {
        console.log('no items in cart')
        return true
    } else {
        console.log('we have items in cart')
        return false
    }
}


const Button = ({history, children, cart_items, customers}) =>
    <button className="btn btn-default btn-block"
            onClick={() => history.push('/shop/checkout')}
            disabled={PaymentEnabled(cart_items, customers)}>
        {console.log('cart items button')}
        {console.log(cart_items)}
        {console.log(cart_items.length)}
        {children}
    </button>

{/* Check for selected customer when one or more school products was selected.. otherwise disable. */}

const CartToolsPayment = ({customers, cart_items, history, intl}) =>
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