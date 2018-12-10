import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"
import validator from 'validator'

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
        this.props.clearSearchValue()
    }

    onSearchChange(e) {
        console.log('search value changed')
        const value = e.target.value
        const products = this.props.products

        this.props.setSearchValue(value)

        console.log("timeout: " + products.searchTimeout)
        if ( products.searchTimeout ) {
            this.props.clearSearchTimeout()
            console.log('reset timeout')
        }

        let timeout
        this.props.setSearchTimeout(
            setTimeout(() => this.setSearchValue(value), 
                (validator.isInt(value)) ? timeout = 225 : timeout = 750)
        )
    }

    setSearchValue(value) {
        console.log('done something :)!')
        console.log(this.props)
        this.props.clearSearchProductID()

        // const barcode_scans = this.props.barcode_scans
        // const memberships = this.props.memberships.data

        // console.log(barcode_scans)
        let productID

        if (validator.isInt(value)) {
            console.log('This is an int!')
            productID = value

            this.props.setSearchProductID(productID)

            console.log('productID')
            console.log(productID)

        } else {
            console.log('not an int value')

        }
        console.log(value)
    }

    
    render() {
        const products = this.props.products
        const products_data = this.props.products_data

        return (
            <ShopTemplate app_state={this.props.app}>
                { this.props.loaded ? 
                    <div>
                        <InputGroupSearch value={products.search_value}
                                          placeholder="Scan barcode or search..."
                                          onClear={this.onSearchClear.bind(this)}
                                          onChange={this.onSearchChange.bind(this)}
                        />
                        <ProductsList products={products_data}
                                      onClick={this.onClickProductListItem.bind(this)} />
                    </div> :
                     "Loading..."
                }
            </ShopTemplate>
        )
    }
}

export default Products
