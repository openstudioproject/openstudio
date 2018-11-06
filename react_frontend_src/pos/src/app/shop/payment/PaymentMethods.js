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

    // populateProducts = (products) => {
    //     let container = []
    //     let children = []

    //     products.map((product, i) => {
    //         children.push(
    //             <ProductsListItem data={product}
    //                               key={"product_" + v4()}
    //                               onClick={() => this.props.onClick(product)}
    //                               />
    //         )
    //         if (( (i+1) % 3 ) === 0 || i+1 == products.length)  {
    //             container.push(<div className="row" key={"row_" + v4()}>{children}</div>)
    //             children = []
    //         }
    //     })
        
    //     return container
    // }

    render() {
        const payment_methods = this.props.methods

        return (
            payment_methods.map((method, i) =>
                <div key={v4()}>
                    {method['Name']}
                </div>
            )
        )
    }
}

export default PaymentMethods

