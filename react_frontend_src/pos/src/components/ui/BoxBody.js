import React from "react"

const BoxBody = ({children, className=""}) =>
    <div className={"box-body " + className}>
        {children}
    </div>

export default BoxBody