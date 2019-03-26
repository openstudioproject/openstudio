import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'
import { Formik, Form, Field, ErrorMessage } from 'formik'

import ExpensesTemplate from "./ExpensesTemplateContainer"
import EXPENSE_SCHEMA from "./yupSchema"

class ExpenseAdd extends Component {
    constructor(props) {
        super(props)
        console.log("Expense Add props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        app: PropTypes.object,
    }

    render() {
        const return_url = '/expenses'

        return (
            <ExpensesTemplate app={this.props.app} expenses={this.props.expenses} setPageTitle={this.props.setPageTitle}>
                <Formik
                    initialValues={{ name: '', code: '' }}
                    validationSchema={EXPENSE_SCHEMA}
                    onSubmit={(values, { setSubmitting }) => {
                        // dispatch actions here


                        // addLocation({ variables: {
                        //     input: {
                        //     name: values.name, 
                        //     code: values.code
                        //     }
                        // }, refetchQueries: [
                        //     {query: GET_COSTCENTERS_QUERY, variables: {"archived": false }}
                        // ]})
                        // .then(({ data }) => {
                        //     console.log('got data', data);
                        //     toast.success((t('finance.costcenters.toast_add_success')), {
                        //         position: toast.POSITION.BOTTOM_RIGHT
                        //         })
                        //     }).catch((error) => {
                        //     toast.error((t('toast_server_error')) + ': ' +  error, {
                        //         position: toast.POSITION.BOTTOM_RIGHT
                        //         })
                        //     console.log('there was an error sending the query', error)
                        //     setSubmitting(false)
                        //     })
                    }}
                    >
                    {({ isSubmitting, errors }) => (
                        <div className="box box-solid">
                            <Form>
                                <div className="box-body">
                                    <label>Amount</label>
                                    <Field type="text" 
                                        name="amount" 
                                        className={(errors.amount) ? "form-control is-invalid" : "form-control"} 
                                        autoComplete="off" />
                                    <ErrorMessage name="amount" component="span" className="invalid-feedback" />
                                    {/* <Form.Group label={t('finance.costcenters.code')}>
                                        <Field type="text" 
                                                name="code" 
                                                className={(errors.code) ? "form-control is-invalid" : "form-control"} 
                                                autoComplete="off" />
                                        <ErrorMessage name="code" component="span" className="invalid-feedback" />
                                    </Form.Group> */}
                                </div>
                                <div className="box-footer">
                                    {/* <Button 
                                        color="primary"
                                        className="pull-right" 
                                        type="submit" 
                                        disabled={isSubmitting}
                                    >
                                        {t('submit')}
                                    </Button>
                                    <Button color="link" onClick={() => history.push(return_url)}>
                                        {t('cancel')}
                                    </Button> */}
                                </div>
                            </Form>
                        </div>
                    )}
                </Formik>
            </ExpensesTemplate>
        )
    }
}

export default ExpenseAdd
