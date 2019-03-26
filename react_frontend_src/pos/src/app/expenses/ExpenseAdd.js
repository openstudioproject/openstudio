import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'

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

        return (
            <ExpensesTemplate app={this.props.app} expenses={this.props.expenses} setPageTitle={this.props.setPageTitle}>
                Form here
            </ExpensesTemplate>
        )
    }
}

export default ExpensesAdd
