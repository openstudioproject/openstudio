import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import ShopTemplate from '../ShopTemplate'
import ProductsList from "./CartList"

class Products extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        app: PropTypes.object,
        items: PropTypes.array
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.products' })
        )
    }
    
    render() {
        const items = this.props.items

        return (
            <div class="box box-solid cart">
                { items.length ? 
                     "we have items on our cart":
                     "The shopping cart is empty"
                }
            </div>
        )
    }
}

export default Products
