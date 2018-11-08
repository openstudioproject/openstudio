import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"


class ButtonValidate extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        selectedID: PropTypes.int
        // setPageTitle: PropTypes.function,
        // app: PropTypes.object,
        // total: PropTypes.int,
    }

    
    render() {
        const selectedID = this.props.selectedID
        const btnClass = (selectedID) ? "btn-success": "btn-default"

        return (
            <button className={ "pull-right btn " + btnClass }
                    disabled={!(selectedID)}
                    onClick={this.props.onClick}>
                Validate { " " }
                <i className="fa fa-angle-double-right"></i>
            </button>
        )
    }
}

export default ButtonValidate
