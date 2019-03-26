import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'
import { Formik, Form as FoForm, Field, ErrorMessage } from 'formik'

import ExpensesTemplate from "./ExpensesTemplate"


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
                    validationSchema={COSTCENTER_SCHEMA}
                    onSubmit={(values, { setSubmitting }) => {
                        addLocation({ variables: {
                            input: {
                            name: values.name, 
                            code: values.code
                            }
                        }, refetchQueries: [
                            {query: GET_COSTCENTERS_QUERY, variables: {"archived": false }}
                        ]})
                        .then(({ data }) => {
                            console.log('got data', data);
                            toast.success((t('finance.costcenters.toast_add_success')), {
                                position: toast.POSITION.BOTTOM_RIGHT
                                })
                            }).catch((error) => {
                            toast.error((t('toast_server_error')) + ': ' +  error, {
                                position: toast.POSITION.BOTTOM_RIGHT
                                })
                            console.log('there was an error sending the query', error)
                            setSubmitting(false)
                            })
                    }}
                    >
                    {({ isSubmitting, errors }) => (
                        <Form>
                            <Card.Body>
                                <Form.Group label={t('name')}>
                                    <Field type="text" 
                                            name="name" 
                                            className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                                            autoComplete="off" />
                                    <ErrorMessage name="name" component="span" className="invalid-feedback" />
                                </Form.Group>
                                <Form.Group label={t('finance.costcenters.code')}>
                                    <Field type="text" 
                                            name="code" 
                                            className={(errors.code) ? "form-control is-invalid" : "form-control"} 
                                            autoComplete="off" />
                                    <ErrorMessage name="code" component="span" className="invalid-feedback" />
                                </Form.Group>
                            </Card.Body>
                            <Card.Footer>
                                <Button 
                                    color="primary"
                                    className="pull-right" 
                                    type="submit" 
                                    disabled={isSubmitting}
                                >
                                    {t('submit')}
                                </Button>
                                <Button color="link" onClick={() => history.push(return_url)}>
                                    {t('cancel')}
                                </Button>
                            </Card.Footer>
                        </Form>
                    )}
                </Formik>
            </ExpensesTemplate>
        )
    }
}

export default ExpenseAdd
