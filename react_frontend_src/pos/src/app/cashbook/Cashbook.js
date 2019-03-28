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
        return (
            <CashbookTemplate />
        )
    }
}

export default Cashbook
