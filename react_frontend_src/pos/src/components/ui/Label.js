import React from "react"

const Label = ({type, children}) =>
    <span className={"label " + type}>{children}</span>

export default Label