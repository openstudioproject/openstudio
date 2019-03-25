import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'

import PageTemplate from "../../components/PageTemplate"
import ExpensesList from "./ExpensesList"


class Expenses extends Component {
    constructor(props) {
        super(props)
        console.log("Expenses props:")
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
        const data = this.props.expenses.data

        return (
            <PageTemplate app_state={this.props.app}>
                {(!this.props.expenses.loaded) ? "Loading expenses..." :
                    <div className="row">
                        <div className="col-md-4">
                            <ExpensesList items={data}/>
                        </div>
                        <div className="col-md-6">
                            Form here?
                        </div>
                    </div>
                }
            </PageTemplate>
        )
    }
}

export default Expenses
