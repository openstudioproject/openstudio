import React from "react"


const PaymentMethodName = ({methods, selected_method}) => {
    let name = ''

    methods.map((method, i) => 
        (method.id === selected_method) ? 
            name = method['Name'] : ''
    )

    return <span>{name}</span>
}

export default PaymentMethodName
