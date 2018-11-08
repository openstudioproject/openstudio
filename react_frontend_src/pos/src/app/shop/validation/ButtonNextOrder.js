import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"


class ButtonNextOrder extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        selectedID: PropTypes.int,
        total: PropTypes.int
        // setPageTitle: PropTypes.function,
        // app: PropTypes.object,
        // total: PropTypes.int,
    }

    
    render() {

        return (
            <button className={ "pull-right btn btn-success" }
                    onClick={this.props.onClick}>
                Next Order { " " }
                <i className="fa fa-angle-double-right"></i>
            </button>
        )
    }
}

export default ButtonNextOrder
