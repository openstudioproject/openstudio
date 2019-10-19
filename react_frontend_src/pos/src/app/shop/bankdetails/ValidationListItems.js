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
                        <th><span className="pull-right">PRICE</span></th>
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
                            <td className="validation-list-amount">
                                <span className="pull-right">
                                    <Currency amount={ item.TotalPriceVAT } />
                                </span>
                            </td>
                        </tr>
                    )
                    }
                </tbody>
                <tfoot>
                    <th></th>
                    <th></th>
                    <th className="validation-list-amount">
                        <span className="pull-right">
                            <Currency amount={total} />
                        </span>
                    </th>
                </tfoot>
            </table>
        )
    }
}

export default ValidationListItems
