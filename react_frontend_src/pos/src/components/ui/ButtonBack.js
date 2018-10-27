import React from "react"

const ButtonBack = ({onClick=f=>f, children}) =>
    <button onClick={onClick} className="btn btn-default">
        <i className="fa fa-chevron-left"></i>
        {children}
    </button>

export default ButtonBack