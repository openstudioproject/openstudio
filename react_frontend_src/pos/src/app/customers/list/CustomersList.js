import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'


class CustomersList extends Component {
    constructor(props) {
        super(props)
        console.log("Customers props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        customers: PropTypes.object,
    }

    componentWillMount() {
    }

    componentDidMount() {
    }

    onChange(e) {
        const value = e.target.value
        const customers = this.props.customers
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


    onClickButtonBack(e) {
        console.log("clicked")
        this.props.history.push('/products/school/classcards')
    }

    render() {
        const customers = this.props.customers
        const intl = this.props.intl

        let customers_display
        if ( customers.searchID ) {
            customers_display = [
                customers.data[customers.searchID]
            ]
        }
        console.log(customers_display)

        return (
            <section>
                List here<br/>
                SearchID: {' '}
                {customers.searchID}
                <br />
                SelectedID: {' '}
                {customers.selectedID}
                <br />

            </section>
        )
    }
}

export default CustomersList
