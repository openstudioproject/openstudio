import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"

import PageTemplate from "../../../components/PageTemplate"
import Box from "../../../components/ui/Box"
import BoxBody from "../../../components/ui/BoxBody"
import BoxHeader from "../../../components/ui/BoxHeader"

import ButtonNextOrder from "./ButtonNextOrder"
import ValidationList from "./ValidationList"


class BankDetails extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        state: PropTypes.object,
        app: PropTypes.object
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.shop.bankdetails.page_title' })
        )
    }


    // onClickNextOrder() {
    //     console.log('next order clicked')

    //     const cartItems = this.props.cart.items
    //     let cartHasClasscard = false
    //     let cartHasMembership = false
    //     let cartHasSubscription = false
    //     let cartHasClassReconcileLater = false
    //     var i
    //     for (i = 0; i < cartItems.length; i++) {
    //         console.log(cartItems[i])
    //         switch (cartItems[i].item_type) {
    //             case "classcard":
    //                 cartHasClasscard = true
    //                 break
    //             case "subscription":
    //                 cartHasSubscription = true
    //                 break
    //             case "membership":
    //                 cartHasMembership = true
    //                 break
    //             case "class_reconcile_later":
    //                 cartHasClassReconcileLater = true
    //         }
    //     } 

    //     if ( (cartHasClasscard) || (cartHasSubscription) || (cartHasMembership) || (cartHasClassReconcileLater) ){
    //         this.props.fetchCustomersSchoolInfo(this.props.selected_customerID)
    //     }
    //     // if (cartHasSubscription) {
    //     //     this.props.fetchCustomersSubscriptions()
    //     // }
    //     // if (cartHasSubscription) {
    //     //     this.props.fetchCustomersMemberships()
    //     //     this.props.fetchCustomersMembershipsToday()
    //     // }

    //     this.props.clearSelectedPaymentMethod()
    //     this.props.clearCartItems()
    //     this.props.clearSelectedCustomer()
    //     //TODO: Add clear functions for cart error & error message, if any.
    //     this.props.history.push('/shop/products')

    // }
    
    render() {
        const app = this.props.app
        console.log('app')
        console.log(app)
        const history = this.props.history

        return (
            <PageTemplate app_state={app}>
                <div className="row">
                    <div className="col-md-4 col-md-offset-4">
                        <Box>
                            <BoxHeader title="Enter bank account information"/>
                            <BoxBody className="">
                                Form goes here...
                            </BoxBody>
                        </Box>
                    </div>
                </div>
            </PageTemplate>
        )
    }
}

export default BankDetails
