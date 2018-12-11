import React from "react"

const ButtonBack = ({onClick=f=>f, children, classAdditional=''}) =>
    <button onClick={onClick} className={"btn btn-default " + classAdditional} >
        <i className="fa fa-angle-double-left"></i> { ' ' }
        {children}
    </button>

export default ButtonBack