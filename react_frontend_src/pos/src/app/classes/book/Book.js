import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"
import { toast } from 'react-toastify'


import ButtonBack from "../../../components/ui/ButtonBack"
import ClassNameDisplay from "../../../components/ui/ClassNameDisplay"
import PageTemplate from "../../../components/PageTemplate"
import BookOptionsList from "./BookOptionsList"

import customerHasRequiredMembership from './customerHasRequiredMembership'


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
        // Always refresh membership today
        this.props.fetchShopMemberships()
        this.props.fetchMembershipsToday(this.props.match.params.customerID)

        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.classes.book_title' })
        )        

        console.log(this.props.match.params.clsID)
        console.log(this.props.match.params.customerID)
        this.props.fetchBookingOptions(this.props.match.params.clsID, this.props.match.params.customerID )
        
    }

    componentDidMount() {
        const classes = this.props.classes
        const clsID = this.props.match.params.clsID

        if (!classes.loaded) {
            this.props.fetchClasses({setPageSubtitle: true, clsID: this.props.match.params.clsID})
        } else {
            this.props.setPageSubtitle(
                <ClassNameDisplay classes={classes.data} clsID={clsID} />
            )
        }
    }

    componentWillUnmount() {
        this.props.setPageSubtitle("")
        this.props.clearMembershipsToday()
    }

    onClickButtonBack() {
        this.props.history.push(`/classes/${this.props.match.params.customerID}`)
        // this.props.history.push(`/classes/attendance/${this.props.match.params.clsID}`)
    }

    addRequiredMembershipToCart(customerID, option) {
        const school_memberships = this.props.school_memberships

        function findMembership(item) {
            return item.id == option.school_memberships_id
        }

        console.log(school_memberships)
        let cart_item = school_memberships.data.find(findMembership)

        let item = {
            id: v4(),
            item_type: 'membership',
            quantity: 1,
            data: cart_item
        }

        console.log('item')
        console.log(item)
        // Check if item not yet in cart
        
        // If not yet in cart, add as a new product, else increase 
        this.props.addShopCartItem(item)
    }

    onClickBookOption(option) {
        console.log('click book option')
        console.log(option)
        console.log(option.Type)

        const clsID = this.props.match.params.clsID
        const customerID = this.props.match.params.customerID

        console.log(clsID)
        console.log(customerID)

        // this.props.checkinCustomer(customerID, clsID, option)

        const customer_memberships = this.props.customer_memberships_today.data
        console.log('customer_memberships')
        console.log(customer_memberships)

        let item

        switch (option.Type) {
            case "classcard_shop":
                console.log('shop action...')

                item = {
                    id: v4(),
                    item_type: 'classcard',
                    quantity: 1,
                    checkin_classes_id: clsID,
                    data: option
                }
                // customer needs to pay
                // clear cart
                this.props.clearShopCart()
                // set shop selected customer id
                this.props.setSelectedCustomerID(customerID)
                this.props.setDisplayCustomerID(customerID)
                // add item to cart

                // If not yet in cart, add as a new product, else increase 
                this.props.addShopCartItem(item)
                // set some value to indicate redirection back to attendance list with notification after validating payment

                if (option.school_memberships_id) {
                    if (!customerHasRequiredMembership(option.school_memberships_id, customer_memberships)) {
                        console.log("Add required membership to cart")
                        this.addRequiredMembershipToCart(customerID, option)
                    }
                }

                // redirect to payment
                this.props.history.push('/shop/products')

                break

            case "subscription_shop":
                console.log('shop action...')

                item = {
                    id: v4(),
                    item_type: 'subscription',
                    quantity: 1,
                    checkin_classes_id: clsID,
                    data: option
                }
                // customer needs to pay
                // clear cart
                this.props.clearShopCart()
                // set shop selected customer id
                this.props.setSelectedCustomerID(customerID)
                this.props.setDisplayCustomerID(customerID)
                // add item to cart

                // If not yet in cart, add as a new product, else increase 
                this.props.addShopCartItem(item)
                // set some value to indicate redirection back to attendance list with notification after validating payment

                if (option.school_memberships_id) {
                    if (!customerHasRequiredMembership(option.school_memberships_id, customer_memberships)) {
                        console.log("Add required membership to cart")
                        this.addRequiredMembershipToCart(customerID, option)
                    }
                }

                // redirect to payment
                this.props.history.push('/shop/products')

                break

            case "dropin_and_membership": 
                console.log('executing dropin & membership code')
                console.log(option)
                // let dropin_price
                // if (customer_memberships) {
                //     dropin_price = option.MembershipPrice
                // } else {
                //     dropin_price = option.Price
                // }
                // console.log(dropin_price)


                // Check if price > 0
                if (option.Price > 0) {
                    // customer needs to pay
                    // clear cart (Disabled for now, customer requisted ability to pay for multiple drop-in classes at once)
                    // this.props.clearShopCart()
                    // set shop selected customer id
                    this.props.setSelectedCustomerID(customerID)
                    this.props.setDisplayCustomerID(customerID)
                    // add item to cart
                    
                    item = {
                        id: v4(),
                        item_type: 'class_dropin',
                        quantity: 1,
                        with_membership: true,
                        data: option
                     }
             
                     console.log('item')
                     console.log(item)
                     // Check if item not yet in cart
                     
                     // If not yet in cart, add as a new product, else increase 
                     this.props.addShopCartItem(item)
                    // set some value to indicate redirection back to attendance list with notification after validating payment

                    if (option.school_memberships_id) {
                        if (!customerHasRequiredMembership(option.school_memberships_id, customer_memberships)) {
                            console.log("Add required membership to cart")
                            this.addRequiredMembershipToCart(customerID, option)
                        }
                    }

                    // redirect to payment
                    this.props.history.push('/shop/products')
                    
                } else {
                    // check-in, price = 0
                    this.props.checkinCustomer(customerID, clsID, option, this.props.history)
                }
                break

            case "dropin": 
                console.log('executing dropin code')
                console.log(option)
                // let dropin_price
                // if (customer_memberships) {
                //     dropin_price = option.MembershipPrice
                // } else {
                //     dropin_price = option.Price
                // }
                // console.log(dropin_price)


                // Check if price > 0
                if (option.Price > 0) {
                    // customer needs to pay
                    // clear cart (Disabled for now, customer requisted ability to pay for multiple drop-in classes at once)
                    // this.props.clearShopCart()
                    // set shop selected customer id
                    this.props.setSelectedCustomerID(customerID)
                    this.props.setDisplayCustomerID(customerID)
                    // add item to cart
                    
                    item = {
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
                    this.props.history.push('/shop/products')
                    
                } else {
                    // check-in, price = 0
                    this.props.checkinCustomer(customerID, clsID, option, this.props.history)
                }
                break
            case "trial": 
                console.log('trial code here')
                let trial_price
                if (customer_memberships) {
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
                    this.props.setSelectedCustomerID(customerID)
                    this.props.setDisplayCustomerID(customerID)
                    // add item to cart
                    
                    item = {
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
                    this.props.history.push('/shop/products')
                    
                } else {
                    // check-in, price = 0
                    this.props.checkinCustomer(customerID, clsID, option, this.props.history)
                }
            
                break
            case "subscription":
                if (option.school_memberships_id) {
                    console.log('membership required')
                    if (customerHasRequiredMembership(option.school_memberships_id, customer_memberships)) {
                        this.props.checkinCustomer(customerID, clsID, option, this.props.history)
                    } else {
                        console.log('redirect to cart to buy the required membership')
                        this.props.clearShopCart()
                        // set shop selected customer id
                        this.props.setSelectedCustomerID(customerID)
                        this.props.setDisplayCustomerID(customerID)

                        this.addRequiredMembershipToCart(customerID, option)
  
                        // redirect to products
                        this.props.history.push('/shop/products')
                    }
                } else {
                    this.props.checkinCustomer(customerID, clsID, option, this.props.history)
                }
                break
            case "classcard":
                // Check membership
                if (option.school_memberships_id) {
                    if (customerHasRequiredMembership(option.school_memberships_id, customer_memberships)) {
                        this.props.checkinCustomer(customerID, clsID, option, this.props.history)
                    } else {
                        console.log('redirect to cart to buy the required membership')
                        this.props.clearShopCart()
                        // set shop selected customer id
                        this.props.setSelectedCustomerID(customerID)
                        this.props.setDisplayCustomerID(customerID)

                        this.addRequiredMembershipToCart(customerID, option)

                        // redirect to products
                        this.props.history.push('/shop/products')
                    }
                } else {
                    this.props.checkinCustomer(customerID, clsID, option, this.props.history)
                }
                break
            case "complementary":
                this.props.checkinCustomer(customerID, clsID, option, this.props.history)
            case "reconcile_later":
                this.props.checkinCustomer(customerID, clsID, option, this.props.history)
            default: 
                console.log("Check-in type not found:")
                console.log(option)
                break
            
        }
    }


    render() {
        const booking_options = this.props.options.data

        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!this.props.options.loaded || !this.props.customer_memberships_today.loaded) ? 
                        <div>Loading booking options, please wait...</div> :
                        <section className="classes_attendance">
                            <ButtonBack onClick={this.onClickButtonBack.bind(this)} 
                                        classAdditional="btn-margin-right">
                                Classes
                            </ButtonBack>
                            <BookOptionsList booking_options={booking_options}
                                             customer_memberships={this.props.customer_memberships_today.data}
                                             onClick={this.onClickBookOption.bind(this)} />
                            {/* <AttendanceList attendance_items={this.props.attendance.data} /> */}
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default Book
