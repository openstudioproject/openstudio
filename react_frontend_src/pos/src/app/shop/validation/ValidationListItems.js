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
        const total = this.props.total

        return (
            <table className='table'>
                <thead>
                    <tr>
                        <th>ITEM</th>
                        <th>QTY</th>
                        <th>PRICE</th>
                    </tr>
                </thead>
                <tbody>
                    {
                    items.map((item, i) =>
                        <tr key={v4()}>
                            <td>
                                {item.ProductName} <br /> 
                                {item.Description}
                            </td>
                            <td>
                                { item.Quantity }
                            </td>
                            <td>
                                <Currency amount={ item.TotalPriceVAT } />
                            </td>
                        </tr>
                    )
                    }
                </tbody>
                <tfoot>
                    <th></th>
                    <th></th>
                    <th><Currency amount={total} /></th>
                </tfoot>
            </table>
        )
    }
}

export default ValidationListItems
