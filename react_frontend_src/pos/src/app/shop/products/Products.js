import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"

import ShopTemplate from '../ShopTemplate'
import ProductsList from "./ProductsList"

import InputGroupSearch from "../../../components/ui/InputGroupSearch"

class Products extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        addToCart: PropTypes.function,
        app: PropTypes.object,
        categories: PropTypes.object,
        loaded: PropTypes.boolean,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.products' })
        )
        this.props.setCustomersListRedirectNext('/shop/products')
    }

    onClickProductListItem(product) {
        console.log('clicked on:')
        console.log(product)

        let item = {
           id: v4(),
           item_type: 'product',
           quantity: 1,
           data: product 
        }

        console.log('item')
        console.log(item)
        // Check if item not yet in cart
        
        // If not yet in cart, add as a new pproduct, else increase 
        this.props.addToCart(item)
        
        // this.props.setDisplayCustomerID(id)
    }

    onSearchClear() {
        console.log('clear clicked')
    }

    onSearchChange(e) {
        console.log('search value changed')
        const value = e.target.value
        const customers = this.props.customers

        this.props.setSearchValue(value)

        console.log("timeout: " + customers.searchTimeout)
        if ( customers.searchTimeout ) {
            this.props.clearSearchTimeout()
            console.log('reset timeout')
        }

        let timeout
        this.props.setSearchTimeout(
            setTimeout(() => this.setSearchValue(value), 
                (validator.isInt(value)) ? timeout = 225 : timeout = 750)
        )
        

    }
    
    render() {
        const products = this.props.products

        return (
            <ShopTemplate app_state={this.props.app}>
                { this.props.loaded ? 
                    <div>
                        <InputGroupSearch value={products.search_value}
                                          placeholder="Scan barcode or search..."
                                          onClear={this.onSearchClear.bind(this)}
                        />
                        <ProductsList products={products}
                                      onClick={this.onClickProductListItem.bind(this)} />
                    </div> :
                     "Loading..."
                }
            </ShopTemplate>
        )
    }
}

export default Products
