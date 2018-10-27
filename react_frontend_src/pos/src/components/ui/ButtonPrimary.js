import React from "react"

const ButtonPrimary = ({classAdditional='', onClick=f=>f, children}) =>
    <button onClick={onClick} className={"btn btn-primary " + classAdditional}>
        {children}
    </button>

export default ButtonPrimary