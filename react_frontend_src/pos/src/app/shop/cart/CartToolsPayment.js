import React from "react"
import { v4 } from "uuid"

const Button = ({history, children}) =>
    <button className="btn btn-default btn-block"
            onClick={() => history.push('/shop/checkout')}>
        {children}
    </button>

{/* Check for selected customer when one or more school products was selected.. otherwise disable. */}

const CartToolsPayment = ({customers, history, intl}) =>
    <div>
        {
            <Button history={history}>
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