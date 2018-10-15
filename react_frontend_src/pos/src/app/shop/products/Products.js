import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import ShopTemplate from '../components/ShopTemplate'
import ProductsList from "./ProductsList"

class Products extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        categories: PropTypes.object,
        loaded: PropTypes.boolean,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.products' })
        )
    }
    
    render() {
        const categories = this.props.categories

        return (
            <ShopTemplate app_state={this.props.app}>
                { this.props.loaded ? 
                     <ProductsList categories={categories} />:
                     "Loading..."
                }
            </ShopTemplate>
        )
    }
}

export default Products
