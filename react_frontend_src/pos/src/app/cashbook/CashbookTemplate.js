import React, { Component } from "react"
import { intlShape, injectIntl } from "react-intl"

import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'

import PageTemplate from "../../components/PageTemplate"
import ExpensesList from "./ExpensesList"
import CashCountsList from "./CashCountsList";


class CashbookTemplate extends Component {
    constructor(props) {
        super(props)
        console.log("Cashbook template props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.cashbook.page_title' })
        )
    }

    render() {
        const cashbook = this.props.cashbook
        const expenses_data = this.props.cashbook.expenses_data
        const history = this.props.history

        return (
            <PageTemplate app_state={this.props.app}>
                {(!this.props.cashbook.expenses_loaded) ? "Loading expenses..." :
                    <div className="row">
                        <div className="col-md-4">
                            <CashCountsList cashbook={cashbook} />
                            <ExpensesList items={expenses_data} />
                        </div>
                        <div className="col-md-8">
                            <div className="row">
                                <div className="col-md-8">
                                    {this.props.children}
                                </div>
                                <div className="col-md-4">
                                    <h4>Cash count</h4>
                                    <button onClick={() => history.push('/cashbook/cashcount/set/opening')}
                                            className="btn btn-primary btn-block">
                                        <i className="fa fa-check-circle-o" /> Set opening balance
                                    </button>
                                    <button onClick={() => history.push('/cashbook/cashcount/set/closing')}
                                            className="btn btn-primary btn-block">
                                        <i className="fa fa-check-circle-o" /> Set closing balance
                                    </button>
                                    <h4>Expenses</h4>
                                    <button onClick={() => history.push('/cashbook/expenses/add')}
                                            className="btn btn-primary btn-block">
                                        <i className="fa fa-plus" /> Add expense
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                }
            </PageTemplate>
        )
    }
}

export default injectIntl(CashbookTemplate)
