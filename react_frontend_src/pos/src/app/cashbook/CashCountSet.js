import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"
import { NavLink } from 'react-router-dom'
import { withRouter } from 'react-router'

import PageTemplate from "../../components/PageTemplate"
import Currency from "../../components/ui/Currency"
import CashbookTemplate from "./CashbookTemplateContainer"
import FormError from "./FormError"


class CashCountSet extends Component {
    constructor(props) {
        super(props)
        console.log("cash count set props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        app: PropTypes.object,
    }

    componentWillMount() {
    }

    onSubmit(e) {
        e.preventDefault()
        console.log('submit cash count')
        

        const type = this.props.match.params.type
        const data = new FormData(e.target)
        data.append('type', type)
        this.props.setCashCount(data, this.props.history)
    }

    render() {
        const history = this.props.history
        const type = this.props.match.params.type
        const error_data = this.props.cashbook.cash_count_set_error_data

        return (
            <CashbookTemplate>
                <div className="box box-solid expenses-list"> 
                    <div className="box-header">
                        <h3 className="box-title">
                            Set {type} count
                        </h3>
                    </div>
                    <form onSubmit={this.onSubmit.bind(this)}>
                        <div className="box-body">
                            <label htmlFor="amount">Count</label>
                            <input 
                                id="amount" 
                                className="form-control"
                                name="amount" 
                                type="text" 
                            />
                            <FormError message={ (error_data.amount) ? error_data.amount : "" } />
                        
                        </div>
                        <div className="box-footer">
                            <button type="submit"
                                    className="btn btn-primary"
                                    disabled={this.props.cashbook.set_cash_count}>
                                Save
                            </button>
                            <button type="button"
                                    className="btn btn-link"
                                    onClick={() => history.push('/cashbook')}>
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </CashbookTemplate>
        )
    }
}

export default CashCountSet
