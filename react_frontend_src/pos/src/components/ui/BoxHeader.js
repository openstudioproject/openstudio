import React from "react"

const BoxHeader = ({children, title, with_border}) =>
    <div className={"box-header" + (with_border) ? " with_border" : ""}>
        <h3 className="box-title">{title}</h3>
        {children}
    </div>

export default BoxHeader