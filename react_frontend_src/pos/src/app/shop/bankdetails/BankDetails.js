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

import axios_os from "../../../utils/axios_os"
import OS_API from "../../../utils/os_api"

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


    onSubmitPaymentInfo(values, setErrors, setSubmitting) {
      console.log('submitted payment info:')
      console.log(values)

      // Do a post here and update local state with errors, if required.

      axios_os.post(OS_API.CUSTOMER_PAYMENT_INFO_UPDATE, values)
        .then(function(response) {
            console.log(response)
            if (response.data.error) {
                setErrors(response.data.result.errors)
                setSubmitting(false)
            } else {
                history.push('/shop/payment')
            }
        })
        .catch(function(error) {
            console.log(error)
            setSubmitting(false)
        })

      // let item = {
      //    id: v4(),
      //    item_type: 'custom',
      //    quantity: 1,
      //    data: custom_item
      // }

      // console.log('item')
      // console.log(item)
      // // Check if item not yet in cart
      
      // // If not yet in cart, add as a new pproduct, else increase 
      // this.props.addToCart(item)
      
      // // this.props.setDisplayCustomerID(id)
  }
    
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
                                { (!selected_customerID) ? "No customer selected, please select an item from the menu to continue..." :
                                    <Formik
                                        initialValues={{ AccountNumber: '', AccountHolder: '' }}
                                        // validate={values => {
                                        //     let errors = {}
                                        //     // Validate product
                                        //     if ((!values.product) || (validator.isEmpty(values.product))) {
                                        //         errors.product = 'Required'
                                        //     } 
                                        //     // Validate description
                                        //     if ((!values.description) || (validator.isEmpty(values.description))) {
                                        //         errors.description = 'Required'
                                        //     }
                                        //     // Validate price
                                        //     if (!values.price) {
                                        //         errors.price = 'Required'
                                        //     } else if (!validator.isFloat(values.price)) {
                                        //         errors.price = 'Please input an amount, use "." as a decimal separator.'
                                        //     }

                                        //     return errors;
                                        // }}
                                        onSubmit={(values, { resetForm, setSubmitting, setErrors }) => {
                                            values.id = selected_customerID

                                            setTimeout(() => {
                                                this.onSubmitPaymentInfo(values, setErrors, setSubmitting)
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
                                                    <label>Account Holder</label>
                                                    <Field className="form-control" type="text" name="AccountHolder" autoComplete="off" />
                                                    <ErrorMessage name="AccountHolder" component="div" />
                                                </div>
                                                <div className="form-group">
                                                    <label>Account Number</label>
                                                    <Field className="form-control" type="text" name="AccountNumber" autoComplete="off" />
                                                    <ErrorMessage name="AccountNumber" component="div" />
                                                </div>
                                                <button className="btn btn-primary pull-right" type="submit" disabled={isSubmitting}>
                                                    Continue <i className="fa fa-chevron-right" />
                                                </button>
                                            </Form>
                                        )}
                                    </Formik>
                                }
                            </BoxBody>
                        </Box>
                    </div>
                </div>
            </PageTemplate>
        )
    }
}

export default BankDetails
