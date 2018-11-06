import React, {Component} from "react"
import { v4 } from "uuid"

// import AttendanceListItem from "./ClasscardsListItem"
// import Box from '../../../../components/ui/Box'
// import BoxBody from '../../../../components/ui/BoxBody'
// import ProductsListItem from "./PaymentListItem"
import Currency from "../../../components/ui/Currency"


class PaymentTotal extends Component {
    constructor(props) {
        super(props)
        console.log(this.props.total)
    }

    render() {
        const total = this.props.total

        return (
            <div>
                <div className="text-green text-center">
                    <h1>
                        <Currency amount={total} />
                    </h1>
                </div>
                <div className="text-center">
                    Please select a payment method.
                </div>
            </div>
        )
    }
}

export default PaymentTotal

