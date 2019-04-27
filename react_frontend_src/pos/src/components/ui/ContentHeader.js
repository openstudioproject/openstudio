import React from "react"

const ContentHeader = ({title, subtitle, children}) =>
    <section className="content-header">
        <div className="pull-right">
            {children}
        </div>
        <h1>
            {title} <small>{subtitle}</small>
        </h1>
    </section>

export default ContentHeader