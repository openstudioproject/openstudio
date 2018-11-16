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
        const selected_method = this.props.selected_method

        return (
            payment_methods.map((method, i) =>
                (selected_method === method.id) ?
                    <button className="btn btn-primary btn-lg btn-block btn-flat"
                            onClick={() => this.props.onClick(method.id)}
                            key={v4()}>
                        {method['Name']}
                    </button> :
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

