import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

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

        const clsID = this.props.match.params.clsID
        const cuID = this.props.match.params.cuID

        // this.props.checkinCustomer(cuID, clsID, option)

        const customer_has_membership = this.customerHasMembership
        switch(option.type) {
            case "dropin": {
                let price
                if (customer_has_membership) {
                    price = option.MembershipPrice
                } else {
                    price = option.Price
                }
                // Check if price > 0
                if (price > 0) {
                    // customer needs to pay
                    // clear cart
                    // add item to cart
                    // set shop selected customer id
                    // set some value to indicate redirection back to attendance list with notification after validating payment
                    // redirect to payment
                    
                } else {
                    // check-in
                    this.props.checkinCustomer(cuID, clsID, option)
                }
            }
            case "trial": {
                
            }
            default: {
                this.props.checkinCustomer(cuID, clsID, option)
            }
        }
        if (option.type === 'subscription' || option.type === 'classcard') {
            
        } else {
            // Drop-in & trial
            
            if (option.type === 'dropin') {
                // determine price for this customer


            } else {
                
            }

        }
    }

    customerHasMembership() {
        let customer_has_membership = false
        const memberships = this.props.memberships.data
            
        var i;
        for (i = 0; i < memberships.length; i++) { 
            if (memberships[i].auth_customer_id === 3327) {
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
