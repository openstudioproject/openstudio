import React, {Component} from "react"
import { v4 } from "uuid"

// import AttendanceListItem from "./ClasscardsListItem"
// import Box from '../../../../components/ui/Box'
// import BoxBody from '../../../../components/ui/BoxBody'
// import ProductsListItem from "./PaymentListItem"
import Currency from "../../../components/ui/Currency"

const paymentMethodName = (methods, selected_method) => {
    let name

    methods.map((method, i) => 
        (method.id === selected_method) ? 
            name = method['Name'] : ''
    )

    return name
}



class PaymentTotal extends Component {
    constructor(props) {
        super(props)
        console.log(this.props.total)
    }

    render() {
        const total = this.props.total
        const methods = this.props.methods
        const selected_method = this.props.selected_method

        return (
            <div>
                { !(selected_method) ?
                    <div className="text-center">
                        <h1>
                            <span  className="text-green">
                                <Currency amount={total} />
                            </span>
                        </h1>
                        Please select a payment method.
                    </div>
                    
                    : 
                    <div>
                        <table className="table table-striped">
                            <thead>
                                <tr>
                                    <th>Due</th>
                                    <th>Tendered</th>
                                    <th>Method</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><Currency amount={total} /></td>
                                    <td><Currency amount={total} /></td>
                                    <td>{paymentMethodName(methods, selected_method)}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                } 
                
            </div>
        )
    }
}

export default PaymentTotal

