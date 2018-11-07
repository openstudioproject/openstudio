import React, {Component} from "react"
import { v4 } from "uuid"

// import AttendanceListItem from "./ClasscardsListItem"
// import Box from '../../../../components/ui/Box'
// import BoxBody from '../../../../components/ui/BoxBody'
// import ProductsListItem from "./PaymentListItem"

class PaymentMethods extends Component {
    constructor(props) {
        super(props)
        console.log(this.props.methods)
    }

    render() {
        const payment_methods = this.props.methods

        return (
            payment_methods.map((method, i) =>
                <button className="btn btn-default btn-lg btn-block btn-flat"
                        onClick={() => this.props.onClick(method.id)}
                        key={v4()}>
                    {method['Name']}
                </button>
            )
        )
    }
}

export default PaymentMethods

