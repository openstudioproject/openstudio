import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import backendHost from "../../../utils/get_hostname"

class ButtonVerify extends Component {
    constructor(props) {
        super(props)
        console.log('button verify')
        console.log(props)
        this.onClick = this.onClick.bind(this);
    }

    PropTypes = {
        intl: intlShape.isRequired,
        teacher_payment: PropTypes.object,
        onClick: PropTypes.function
    }

    onClick() {
        this.props.onClick()
    }
    
    render() {
        const tp = this.props.teacher_payment
        const export_url = backendHost + '/classes/revenue_export?clsID=' + tp.data.classes_id + '&date=' + tp.data.ClassDate

        return (
            (tp.data.Status === 'verified') ?
            <a className="btn btn-default btn-block" 
               href={export_url}>
                <i className="fa fa-print"></i> { ' ' }
                {this.props.intl.formatMessage({ id:"app.general.strings.pdf" })}
            </a> :
            <button disabled={(tp.error || tp.teacher_payment_verifying)} 
                    onClick={this.onClick}
                    className="btn bg-olive btn-flat btn-block">
                {(this.props.teacher_payment_verifying) ? 
                    <i className="fa fa-refresh fa-spin fa-fw"></i> : 
                    <b>{this.props.intl.formatMessage({ id:"app.general.strings.verify" })}</b>
                }
            </button>
        )
    }
}




export default ButtonVerify