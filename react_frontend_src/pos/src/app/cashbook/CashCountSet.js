import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"
import { NavLink } from 'react-router-dom'
import { withRouter } from 'react-router'

import PageTemplate from "../../components/PageTemplate"
import Currency from "../../components/ui/Currency"
import CashbookTemplate from "./CashbookTemplateContainer"


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
        this.props.setCashCount(data)


        console.log(data.values())
    }

    render() {
        const history = this.props.history
        const type = this.props.match.params.type

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
                            <label htmlFor="Amount">Count</label>
                            <input 
                                id="Amount" 
                                className="form-control"
                                name="Amount" 
                                type="text" 
                            />
                            {/* <CustomerFormError message={ (error_data.first_name) ? error_data.first_name : "" } /> */}
                        
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
