import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"
import { Formik, Form, Field, ErrorMessage, validateYupSchema } from 'formik'

import PageTemplate from "../../../components/PageTemplate"
import Box from "../../../components/ui/Box"
import BoxBody from "../../../components/ui/BoxBody"
import BoxHeader from "../../../components/ui/BoxHeader"

import ButtonNextOrder from "./ButtonNextOrder"


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
        const customers = this.props.customers
        const selected_customerID = this.props.selected_customerID
        const customer = customers[selected_customerID]

        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.shop.bankdetails.page_title' })
        )

        if (customer) {
            this.props.setPageSubtitle(customer.display_name)
        }
    }

    componentWillUnmount() {
        this.props.setPageSubtitle("")
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
        const customers = this.props.customers
        const selected_customerID = this.props.selected_customerID
        const customer = customers[selected_customerID]
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
                              form here...
                                {/* <Formik
                                    initialValues={{ product: '', description: '', price: '0', tax_rates_id: "" }}
                                    validate={values => {
                                        let errors = {};
                                        // Validate product
                                        if ((!values.product) || (validator.isEmpty(values.product))) {
                                            errors.product = 'Required'
                                        } 
                                        // Validate description
                                        if ((!values.description) || (validator.isEmpty(values.description))) {
                                            errors.description = 'Required'
                                        }
                                        // Validate price
                                        if (!values.price) {
                                            errors.price = 'Required'
                                        } else if (!validator.isFloat(values.price)) {
                                            errors.price = 'Please input an amount, use "." as a decimal separator.'
                                        }

                                        return errors;
                                    }}
                                    onSubmit={(values, { resetForm, setSubmitting }) => {
                                        values.id = v4()
                                        values.price = parseFloat(values.price)

                                        setTimeout(() => {
                                            this.onSubmitCustomItem(values)
                                            resetForm()
                                            setSubmitting(false)
                                        }, 400)

                                        
                                        // setTimeout(() => {
                                        // alert(JSON.stringify(values, null, 2));
                                        // setSubmitting(false);
                                        // }, 40);
                                    }}
                                    >
                                    {({ values, handleBlur, handleChange, isSubmitting }) => (
                                        <Form>
                                            <div className="form-group">
                                                <label>Product name</label>
                                                <Field className="form-control" type="text" name="product" autoComplete="off" />
                                                <ErrorMessage name="product" component="div" />
                                            </div>
                                            <div className="form-group">
                                                <label>Description</label>
                                                <Field className="form-control" type="text" name="description" autoComplete="off" />
                                                <ErrorMessage name="description" component="div" />
                                            </div>
                                            <div className="form-group">
                                                <label>Price (incl. Taxes)</label>
                                                <Field className="form-control" type="" name="price" autoComplete="off" />
                                                <ErrorMessage name="price" component="div" />
                                            </div>
                                            <div className="form-group">
                                                <label>Taxes</label>
                                                <select
                                                    name="tax_rates_id"
                                                    value={values.tax_rates_id}
                                                    onChange={handleChange}
                                                    onBlur={handleBlur}
                                                    className="form-control"
                                                >
                                                    <option key={v4()} value="" label="Select tax..." />
                                                    {taxRates.map((rate, i) => {
                                                        return <option key={v4()} value={rate.id}>{rate.Name}</option>
                                                    })}
                                                </select>
                                                <ErrorMessage name="tax_rates_id" component="div" />
                                            </div>
                                            <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                                                Add to cart
                                            </button>
                                        </Form>
                                    )}
                                </Formik> */}
                            </BoxBody>
                        </Box>
                    </div>
                </div>
            </PageTemplate>
        )
    }
}

export default BankDetails
