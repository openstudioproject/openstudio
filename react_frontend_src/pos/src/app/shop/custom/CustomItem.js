import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"
import validator from 'validator'
import { Formik, Form, Field, ErrorMessage } from 'formik';

import ShopTemplate from '../ShopTemplate'

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
   
    
    render() {

        return (
            <ShopTemplate app_state={this.props.app}>
                { this.props.loaded ? 
                    <div>
                        <Formik
                            initialValues={{ product: '', description: '', price: 0, quantity: 1 }}
                            validate={values => {
                                let errors = {};
                                if (!values.product) {
                                    errors.product = 'Required';
                                } 
                                // else if (
                                // !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(values.email)
                                // ) {
                                // errors.email = 'Invalid email address';
                                // }
                                if (!values.description) {
                                    errors.description = 'Required'
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
                                        <Field className="form-control" type="text" name="price" autoComplete="off" />
                                        <ErrorMessage name="price" component="div" />
                                    </div>
                                    <div className="form-group">
                                        <label>Quantity</label>
                                        <Field className="form-control" type="number" name="quantity" autoComplete="off" />
                                        <ErrorMessage name="quantity" component="div" />
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
