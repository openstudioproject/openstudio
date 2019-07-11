import React, { Component } from "react"


class PaymentMethodName extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    componentWillMount() {
        
    }

    render() {
        const methods = this.props.methods
        const selected_method = this.props.selected_method

        let name = ''

        methods.map((method, i) => 
            (method.id === selected_method) ? 
                name = method['Name'] : ''
        )
    
        return <span>{name}</span>
    }

}


// const PaymentMethodName = ({methods, selected_method}) => {
//     let name = ''

//     methods.map((method, i) => 
//         (method.id === selected_method) ? 
//             name = method['Name'] : ''
//     )

//     return <span>{name}</span>
// }

export default PaymentMethodName
