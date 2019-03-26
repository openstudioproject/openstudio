import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'

import PageTemplate from "../../components/PageTemplate"
import ExpensesTemplate from "./ExpensesTemplate"


class Expenses extends Component {
    constructor(props) {
        super(props)
        console.log("Expenses props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        app: PropTypes.object,
        expenses: PropTypes.object
    }

    render() {

        return (
            <ExpensesTemplate app={this.props.app} expenses={this.props.expenses} setPageTitle={this.props.setPageTitle}>
                Hello world!
            </ExpensesTemplate>
        )
    }
}

export default Expenses
