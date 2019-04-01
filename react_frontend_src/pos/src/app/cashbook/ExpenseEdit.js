import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { Formik, Form, Field, ErrorMessage } from 'formik'

import CashbookTemplate from "./CashbookTemplateContainer"
import FormError from "./FormError"
import { v4 } from "uuid"

class ExpenseEdit extends Component {
    constructor(props) {
        super(props)
        console.log("Expense Add props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        app: PropTypes.object,
    }

    onSubmit(e) {
        e.preventDefault()

        console.log("submitted expense add")
        const data = new FormData(e.target)

        this.props.createExpense(data, this.props.history)
    }

    render() {
        const history = this.props.history
        const error_data = this.props.error_data
        console.log(error_data)
        const return_url = '/cashbook'
        const tax_rates = this.props.app.tax_rates

        return (
            <CashbookTemplate app={this.props.app} expenses={this.props.expenses} setPageTitle={this.props.setPageTitle}>
                <div className="box box-solid">
                    <div className='box-header'>
                        <h3 className="box-title">Add expense</h3>
                    </div>
                    <form onSubmit={this.onSubmit.bind(this)}>
                        <div className="box-body">
                            <label htmlFor="Description">Description</label>
                            <input 
                                id="description" 
                                className="form-control"
                                name="Description" 
                                type="text" 
                            />
                            <FormError message={ (error_data.Description) ? error_data.Description : "" } />
                            <label htmlFor="amount">Amount</label>
                            <input 
                                id="Amount" 
                                className="form-control"
                                name="Amount" 
                                type="text" 
                            />
                            <FormError message={ (error_data.Amount) ? error_data.Amount : "" } />
                            <label htmlFor="tax_rates_id">Tax rate</label>
                            <select 
                                id="tax_rates_id" 
                                className="form-control"
                                name="tax_rates_id" 
                            >
                            {
                                tax_rates.map((rate, i) => 
                                    <option value={rate.id} key={v4()}>{rate.Name}</option>
                                )
                            }
                            </select>
                            <FormError message={ (error_data.tax_rates_id) ? error_data.tax_rates_id : "" } />
                            <label htmlFor="YourReference">Reference</label>
                            <input 
                                id="YourReference" 
                                className="form-control"
                                name="YourReference" 
                                type="text" 
                            />
                            <span className="help-block">eg. The invoice or receipt number of a delivery from a supplier</span>
                            <FormError message={ (error_data.YourReference) ? error_data.YourReference : "" } />
                            <label htmlFor="Note">Note</label>
                            <textarea 
                                id="Note" 
                                className="form-control"
                                name="Note" 
                                type="text" 
                            />
                            <FormError message={ (error_data.Note) ? error_data.Note : "" } />
                        </div>
                        <div className="box-footer">
                            <button className="btn btn-primary"
                                    type="submit">
                                Save
                            </button>
                            <button className="btn btn-link"
                                    type="button"
                                    onClick={() => history.push(return_url)}>
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </CashbookTemplate>
        )
    }
}

export default withRouter(ExpenseEdit)

