import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"

import Currency from "../../../components/ui/Currency"
import PaymentMethodName from "../components/PaymentMethodNameContainer"
import ValidationListItems from "./ValidationListItems"


class ValidationList extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        items: PropTypes.array,
        total: PropTypes.int,
        selected_method: PropTypes.int,
    }

    render() {
        const app = this.props.app
        const items = this.props.items
        const total = this.props.total
        const selected_method = this.props.selected_method

        const d = new Date()

        return (
            <div>
                <ValidationListItems items={items} />
                Date: {d.getDay() + "-" + d.getMonth() + "-" + d.getFullYear()}<br />
                Cashier: {app.user.profile.id} <br />
                Payment Method: <PaymentMethodName /> <br />
                Total: <Currency amount={total} />

            </div>
        )
    }
}

export default ValidationList
