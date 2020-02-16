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
        let selected_method = this.props.selected_method
        if (!selected_method) {
            selected_method = this.props.payment_method_id
        }        

        let name = ''

        methods.map((method, i) => 
            (method.id == selected_method) ? 
                name = method['Name'] : ''
        )
    
        return <span>{name}</span>
    }

}


export default PaymentMethodName
