import React from "react"

const Breadcrumb = ({children, onClick=f=>f}) =>
    <ol className="breadcrumb">
        <li onClick={onClick}>
            <span><i className="fa fa-home"></i></span>
        </li>
        {children}
    </ol>

export default Breadcrumb