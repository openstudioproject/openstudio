import React from "react"

const ContentHeader = ({title, subtitle, children}) =>
    <section className="content-header">
        <h1>
            {title} <small>{subtitle}</small>
        </h1>
        {children}
    </section>

export default ContentHeader