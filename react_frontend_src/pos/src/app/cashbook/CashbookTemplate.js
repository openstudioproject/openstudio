import React, { Component } from "react"
import { intlShape, injectIntl } from "react-intl"

import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'

import PageTemplate from "../../components/PageTemplate"
import ExpensesList from "./ExpensesList"
import BalanceList from "./BalanceList";


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
            this.props.intl.formatMessage({ id: 'app.pos.expenses.page_title' })
        )
    }

    render() {
        const expenses_data = this.props.cashbook.expenses_data

        return (
            <PageTemplate app_state={this.props.app}>
                {(!this.props.cashbook.expenses_loaded) ? "Loading expenses..." :
                    <div className="row">
                        <div className="col-md-4">
                            <BalanceList  />
                            <ExpensesList items={expenses_data} />
                        </div>
                        <div className="col-md-8">
                            {this.props.children}
                        </div>
                    </div>
                }
            </PageTemplate>
        )
    }
}

export default injectIntl(CashbookTemplate)
