import React from "react"

const BoxHeader = ({children, title}) =>
    <div className={"box-header"}>
        <h3 className="box-title">{title}</h3>
        {children}
    </div>

export default BoxHeader