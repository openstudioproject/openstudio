import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'

import CashbookTemplate from "./CashbookTemplateContainer"


class Cashbook extends Component {
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
        const history = this.props.history

        return (
            <CashbookTemplate>
                <button onClick={() => history.push('expenses/add')}
                        className="btn btn-primary pull-right">
                    <i className="fa fa-plus" /> Add expense
                </button>
                Select an expense from the list to edit it and click the add button to add a new one. 

            </CashbookTemplate>
        )
    }
}

export default Cashbook
