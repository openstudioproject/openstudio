import React from "react"

const ButtonCustomerAdd = ({classAdditional='', onClick=f=>f, children}) =>
    <button onClick={onClick} className={"btn btn-primary " + classAdditional}>
        <i className="fa fa-user"></i>
        <i className="fa fa-plus"></i>
        {children}
    </button>

export default ButtonCustomerAdd