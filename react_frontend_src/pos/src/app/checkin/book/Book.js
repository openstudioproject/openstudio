import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"

import ButtonBack from "../../../components/ui/ButtonBack"
import PageTemplate from "../../../components/PageTemplate"
import BookOptionsList from "./BookOptionsList"



class Book extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        fetchBookingOptions: PropTypes.function,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        options: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.checkin.page_title' })
        )

        console.log(this.props.match.params.clsID)
        console.log(this.props.match.params.cuID)
        this.props.fetchBookingOptions(this.props.match.params.clsID, this.props.match.params.cuID )
    }

    onClickButtonBack() {
        this.props.history.push(`/checkin/attendance/${this.props.match.params.clsID}`)
    }

    onClickBookOption(option) {
        console.log('click book option')
        console.log(option)
        console.log(option.Type)

        const clsID = this.props.match.params.clsID
        const cuID = this.props.match.params.cuID

        // this.props.checkinCustomer(cuID, clsID, option)

        const customer_has_membership = this.customerHasMembership(this.props.match.params.cuID)
        console.log(customer_has_membership)
        switch (option.Type) {
            case "dropin": 
                console.log('executing dropin code')
                let dropin_price
                if (customer_has_membership) {
                    dropin_price = option.MembershipPrice
                } else {
                    dropin_price = option.Price
                }
                console.log(dropin_price)

                // Check if price > 0
                if (dropin_price > 0) {
                    // customer needs to pay
                    // clear cart
                    this.props.clearShopCart()
                    // set shop selected customer id
                    this.props.setSelectedCustomerID(this.props.match.params.cuID)
                    this.props.setDisplayCustomerID(this.props.match.params.cuID)
                    // add item to cart
                    
                    let item = {
                        id: v4(),
                        item_type: 'class_dropin',
                        quantity: 1,
                        data: option
                     }
             
                     console.log('item')
                     console.log(item)
                     // Check if item not yet in cart
                     
                     // If not yet in cart, add as a new product, else increase 
                     this.props.addShopCartItem(item)
                    // set some value to indicate redirection back to attendance list with notification after validating payment

                    // redirect to payment
                    this.props.history.push('/shop/payment')
                    
                } else {
                    // check-in, price = 0
                    this.props.checkinCustomer(cuID, clsID, option, this.props.history)
                }
                break
            case "trial": 
                console.log('trial code here')
                let trial_price
                if (customer_has_membership) {
                    trial_price = option.MembershipPrice
                } else {
                    trial_price = option.Price
                }
                console.log(trial_price)

                // Check if price > 0
                if (trial_price > 0) {
                    // customer needs to pay
                    // clear cart
                    this.props.clearShopCart()
                    // set shop selected customer id
                    this.props.setSelectedCustomerID(this.props.match.params.cuID)
                    this.props.setDisplayCustomerID(this.props.match.params.cuID)
                    // add item to cart
                    
                    let item = {
                        id: v4(),
                        item_type: 'class_trial',
                        quantity: 1,
                        data: option
                     }
             
                     console.log('item')
                     console.log(item)
                     // Check if item not yet in cart
                     
                     // If not yet in cart, add as a new product, else increase 
                     this.props.addShopCartItem(item)
                    // set some value to indicate redirection back to attendance list with notification after validating payment

                    // redirect to payment
                    this.props.history.push('/shop/payment')
                    
                } else {
                    // check-in, price = 0
                    this.props.checkinCustomer(cuID, clsID, option, this.props.history)
                }
            
                break
            case "subscription":
                this.props.checkinCustomer(cuID, clsID, option, this.props.history)
                break
            case "classcard":
                this.props.checkinCustomer(cuID, clsID, option, this.props.history)
                break
            default: 
                console.log("Login type not found:")
                console.log(option)
                break
            
        }
    }

    customerHasMembership(cuID) {
        let customer_has_membership = false
        const memberships = this.props.memberships.data
            
        var i;
        for (i = 0; i < memberships.length; i++) { 
            if (memberships[i].auth_customer_id === cuID) {
                customer_has_membership = true
            }
        }

        return customer_has_membership
    
    }

    render() {
        const cuID = this.props.match.params.cuID
        const booking_options = this.props.options.data
        
        const customer_has_membership = this.customerHasMembership
        

        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!this.props.options.loaded || !this.props.memberships.loaded) ? 
                        <div>Loading booking options, please wait...</div> :
                        <section className="checkin_attendance">
                            <ButtonBack onClick={this.onClickButtonBack.bind(this)} 
                                        classAdditional="btn-margin-right">
                                Attendance
                            </ButtonBack>
                            <BookOptionsList booking_options={booking_options}
                                             customer_has_membership={customer_has_membership}
                                             onClick={this.onClickBookOption.bind(this)} />
                            {/* <AttendanceList attendance_items={this.props.attendance.data} /> */}
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default Book
