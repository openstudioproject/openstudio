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
        const selectedID = this.props.selectedID
        const total = this.props.total
        const btnClass = (selectedID) && (total > 0) ? "btn-success": "btn-default"

        console.log(!(selectedID))
        console.log(total > 0)
        console.log(!(selectedID) && total > 0)

        return (
            <button className={ "pull-right btn " + btnClass }
                    disabled={ (!(selectedID) || (total <= 0)) }
                    onClick={this.props.onClick}>
                Validate { " " }
                <i className="fa fa-angle-double-right"></i>
            </button>
        )
    }
}

export default ButtonNextOrdere
