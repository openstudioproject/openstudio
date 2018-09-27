import React from "react"

const ButtonCustomerEdit = ({classAdditional='', onClick=f=>f, children}) =>
    <button onClick={onClick} className={"btn btn-default " + classAdditional}>
        <i className="fa fa-pencil"></i>
        {children}
    </button>

export default ButtonCustomerEdit