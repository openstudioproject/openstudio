import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'
import validator from 'validator'


import PageTemplate from "../../../components/PageTemplate"
import InputGroupSearch from "../../../components/ui/InputGroupSearch"
import ButtonBack from "../../../components/ui/ButtonBack"
import ButtonPrimary from "../../../components/ui/ButtonPrimary"
import ButtonCustomerAdd from "../../../components/ui/ButtonCustomerAdd"

import CustomersList from "./CustomersList"
import CustomerDisplay from "./CustomerDisplay"
import CustomerFormCreate from "./CustomerFormCreate"
import CustomerFormUpdate from "./CustomerFormUpdate"

class Customers extends Component {
    constructor(props) {
        super(props)
        console.log("Customers props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        customers: PropTypes.object,
        customers_barcodes: PropTypes.string
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.customers.page_title' })
        )
    }

    componentDidMount() {

    }

    setSearchValue(value) {
        console.log('done something :)!')
        console.log(this.props)
        this.props.clearDisplayCustomerID()
        this.props.clearSearchCustomerID()
        this.props.clearSelectedCustomerID()

        const barcode_scans = this.props.barcode_scans
        const memberships = this.props.memberships.data

        console.log(barcode_scans)
        let cuID

        if (validator.isInt(value)) {
            console.log('This is an int!')
            if (barcode_scans == 'membership_id') {
                // find customer ID
                console.log('looking for cuID in memberships')
                for (const key of Object.keys(memberships)) {
                    let m = memberships[key]
                    console.log(m)
                    if ( m['date_id'] == value) {
                        cuID = m['auth_customer_id']
                    }

                }
            } else {
                cuID = value
            }

            this.props.setDisplayCustomerID(cuID)
            this.props.setSearchCustomerID(cuID)

            console.log('customerID')
            console.log(cuID)

        } else {
            console.log('not an int value')

        }

        console.log(value)
    }

    onChange(e) {
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

    onClear(e) {
        this.props.clearSearchValue()
        this.props.clearDisplayCustomerID()
    }

    onClickAdd(e) {
        this.props.clearDisplayCustomerID()
        this.props.clearSelectedCustomerID()
        this.props.clearSearchValue()
        this.props.setUpdateCustomerStatus(false)
        this.props.setCreateCustomerStatus(!this.props.customers.create_customer)
    }

    onClickEdit(e) {
        this.props.setUpdateCustomerStatus(!this.props.customers.update_customer)
    }

    onClickSetCustomer(e) {
        console.log('set customer clicked')
        this.props.setSelectedCustomerID(this.props.customers.displayID)
    }

    onClickDeselectCustomer(e) {
        console.log('Deselect customer clicked')
        this.props.clearSelectedCustomerID()
    }

    onClickButtonBack(e) {
        console.log("clicked")
        this.props.history.push('/products/school/classcards')
    }

    onCreateCustomer(e) {
        console.log('submit user')
        e.preventDefault()
        console.log(e.target)
        const data = new FormData(e.target)

        console.log(data.values())
        this.props.createCustomer(data)
    }

    onUpdateCustomer(e) {
        console.log('submit user')
        e.preventDefault()
        console.log(e.target)
        const data = new FormData(e.target)

        data.set('id', this.props.customers.displayID)
        console.log(data.values())
        this.props.updateCustomer(data)
    }

    onClickCustomersListItem(id) {
        console.log('clicked')
        console.log(id)
        this.props.setDisplayCustomerID(id)
    }

    render() {
        const customers = this.props.customers
        const intl = this.props.intl
        const memberships = this.props.memberships

        let customers_display = []
        if (customers.loaded && memberships.loaded) {
            if ( customers.searchID ) {
                customers_display = [
                    customers.data[customers.searchID]
                ]
            } else if (customers.search_value && customers.search_value.length > 1) {
            Object.keys(customers.data).map( (key) => {
                    //console.log('customer:')
                    //console.log(key)
                    //console.log(customers.data[key])
                    if (customers.data[key].search_name.includes(customers.search_value)) {
                        customers_display.push(customers.data[key])
                    }
                })
            }
        }
        console.log(customers_display)

        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!customers.loaded || !memberships.loaded) ? 
                        <div>{intl.formatMessage({ id: 'app.pos.customers.loading_message' })}</div> :
                        <section className="customers_main">
                            <ButtonBack onClick={this.onClickButtonBack.bind(this)}>
                                Cancel
                            </ButtonBack>
                            <InputGroupSearch placeholder={this.props.intl.formatMessage({ id: 'app.general.placeholders.search' })}
                                              onChange={this.onChange.bind(this)}
                                              onClear={this.onClear.bind(this)}
                                              value={customers.search_value} /> <br />
                            <ButtonCustomerAdd onClick={this.onClickAdd.bind(this)}/>
                            
                            { (customers.displayID) && !(customers.selectedID) ? 
                                <ButtonPrimary onClick={this.onClickSetCustomer.bind(this)}>
                                    Select customer
                                </ButtonPrimary> : ''
                            }
                            { (customers.displayID) && (customers.selectedID) ?
                                <ButtonPrimary onClick={this.onClickDeselectCustomer.bind(this)}>
                                    Deselect customer
                                </ButtonPrimary> : ''   
                            }
                            <CustomerDisplay customerID={customers.displayID}
                                             customers={customers.data} 
                                             edit_in_progress={customers.update_customer}
                                             onClickEdit={this.onClickEdit.bind(this)} />
                            { (customers.create_customer) ?
                                <CustomerFormCreate error_data={customers.create_customer_error_data}
                                                    onSubmit={this.onCreateCustomer.bind(this)}
                                                    onCancel={this.onClickAdd.bind(this)} /> : ''
                            }
                            <CustomerFormUpdate display={customers.update_customer}
                                                error_data={customers.update_customer_error_data}
                                                customerID={customers.displayID}
                                                customers={customers.data}
                                                onCancel={this.onClickEdit.bind(this)}
                                                onSubmit={this.onUpdateCustomer.bind(this)} 
                                                />

                            <CustomersList customers={customers_display}
                                           intl={intl}
                                           onClick={this.onClickCustomersListItem.bind(this)} />
                            {/* <AttendanceList attendance_items={this.props.attendance.data} /> */}
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default Customers
