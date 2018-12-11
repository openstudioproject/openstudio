import React from "react"

const Breadcrumb = ({children, categories, category_filter_id, onClickHome=f=>f}) =>
    <ol className="breadcrumb">
        <li onClick={onClickHome}
            title="Clear category filter">
            <span><i className="fa fa-home"></i></span>
        </li>
        { (category_filter_id) ?
            <li>{categories[category_filter_id].Name}</li> : ''
        }
        {children}
    </ol>

export default Breadcrumb