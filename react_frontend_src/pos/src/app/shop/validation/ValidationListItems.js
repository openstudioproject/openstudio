import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"

import Currency from "../../../components/ui/Currency"
import PaymentMethodName from "../components/PaymentMethodNameContainer"


class ValidationListItems extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        items: PropTypes.array,
    }

    render() {
        const items = this.props.items

        return (
            <table className='table'>
                <tbody>
                    <tr>
                        <td>ITEM</td>
                        <td>QTY</td>
                        <td>PRICE</td>
                    </tr>

                    {
                    items.map((item, i) =>
                        <tr key={v4()}>
                            <td>
                                { 
                                    (item.item_type === 'product') ? 
                                        item.data.variant_name + " (" + item.data.product_name + ")": 
                                        item.data.Name 
                                }
                            </td>
                            <td>
                                { item.quantity }
                            </td>
                            <td>
                                <Currency amount={ (item.item_type === 'product') ? 
                                        item.data.price : 
                                        item.data.Price } 
                                />
                            </td>
                        </tr>
                    )
                    }
                </tbody>
            </table>
        )
    }
}

export default ValidationListItems
