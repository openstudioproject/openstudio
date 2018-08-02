import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"


class ButtonVerify extends Component {
    constructor(props) {
        super(props)
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
        return (
            (this.props.teacher_payment_verifying) ? 'verifying...' :
                (this.props.teacher_payment.data.Status === 'verified') ?
                <div className="text-center">
                    <i className="text-green fa fa-check"></i> { ' ' }
                    {this.props.intl.formatMessage({ id:"app.pos.checkin.revenue.total.verified" })}
                </div> :
                <button disabled={(this.props.teacher_payment.status === 'error')} 
                        onClick={this.onClick}
                        className="btn bg-olive btn-flat btn-block">
                    <b>{this.props.intl.formatMessage({ id:"app.general.strings.verify" })}</b>
                </button>
        )
    }
}




export default ButtonVerify