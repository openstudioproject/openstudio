import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import Currency from "../../../components/ui/Currency"


class CartListTotal extends Component {
    constructor(props) {
        super(props)
        // console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        items: PropTypes.array,
    }

    calculateTotal(items) {
        let total = 0
        items.map((item, i) => {
            if (item.item_type == 'product') {
                if (item.data.price) {
                    total = total + item.data.price
                }
            } else {
                if (item.data.Price) {
                    total = total + item.data.Price 
                }
            }
        })

        return total
    }
    
    render() {
        const items = this.props.items
        let total = this.calculateTotal(items)

        return (
            <div className="pull-right">
                Total:  <Currency amount={total} />
            </div>
        )
    }
}

export default CartListTotal

