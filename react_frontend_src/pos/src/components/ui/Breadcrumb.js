import React from "react"

const Breadcrumb = ({children, onClickHome=f=>f}) =>
    <ol className="breadcrumb">
        <li onClick={onClickHome}>
            <span><i className="fa fa-home"></i></span>
        </li>
        {children}
    </ol>

export default Breadcrumb