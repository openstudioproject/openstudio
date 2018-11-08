import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"


import Box from "../../../components/ui/Box"
import BoxBody from "../../../components/ui/BoxBody"

import ButtonNextOrder from "./ButtonNextOrder"
import Currency from "../../../components/ui/Currency"


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
        const items = this.props.items
        const total = this.props.total
        const selected_method = this.props.selected_method

        return (
            <div>
                Total: <Currency amount={total} />
            </div>
        )
    }
}

export default ValidationList
