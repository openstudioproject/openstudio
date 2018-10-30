import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import CartList from "./CartList"

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
            items.length ? 
            <CartList items={items} />:
            "The shopping cart is empty"
                
        )
    }
}

export default Products
