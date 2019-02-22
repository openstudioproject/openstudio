import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"
import validator from 'validator'
import { Formik, Form, Field, ErrorMessage, validateYupSchema } from 'formik';

import ShopTemplate from '../ShopTemplate'
import ErrorScreen from "../../../components/ui/ErrorScreen";

class CustomItem extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        addToCart: PropTypes.function,
        app: PropTypes.object,
        loaded: PropTypes.boolean,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.products' })
        )
        this.props.setCustomersListRedirectNext('/shop/custom')
    }
   

    onSubmitCustomItem(custom_item) {
        console.log('submitted custom item:')
        console.log(custom_item)

        let item = {
           id: v4(),
           item_type: 'custom',
           quantity: 1,
           data: custom_item
        }

        console.log('item')
        console.log(item)
        // Check if item not yet in cart
        
        // If not yet in cart, add as a new pproduct, else increase 
        this.props.addToCart(item)
        
        // this.props.setDisplayCustomerID(id)
    }
    
    render() {
        const taxRates = this.props.app.tax_rates

        return (
            <ShopTemplate app_state={this.props.app}>
                { this.props.loaded ? 
                    <div>
                        {/* <Formik
                            initialValues={{ email: '', password: '' }}
                            validate={values => {
                            let errors = {};
                            if (!values.email) {
                                errors.email = 'Required';
                            } else if (
                                !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(values.email)
                            ) {
                                errors.email = 'Invalid email address';
                            }
                            return errors;
                            }}
                            onSubmit={(values, { setSubmitting }) => {
                            setTimeout(() => {
                                alert(JSON.stringify(values, null, 2));
                                setSubmitting(false);
                            }, 400);
                            }}
                        >
                            {({ isSubmitting }) => (
                            <Form>
                                <Field type="email" name="email" />
                                <ErrorMessage name="email" component="div" />
                                <Field type="password" name="password" />
                                <ErrorMessage name="password" component="div" />
                                <button type="submit" disabled={isSubmitting}>
                                Submit
                                </button>
                            </Form>
                            )}
                        </Formik> */}
                        <Formik
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
                                        <label>Price</label>
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
                                            {/* Add items here using a loop through tax rates */}
                                            <option value="" label="Select tax..." />
                                            <option value="1" label="0%" />
                                            <option value="2" label="9%" />
                                            <option value="3" label="21%" />
                                        </select>
                                        <ErrorMessage name="tax_rates_id" component="div" />
                                    </div>
                                    <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                                        Add to cart
                                    </button>
                                </Form>
                            )}
                        </Formik>
                    </div> :
                     "Loading..."
                }
            </ShopTemplate>
        )
    }
}

export default CustomItem
