import React from "react"

const ContentHeader = ({title, children}) =>
    <section className="content-header">
        <h1>
            {title}
        </h1>
        {children}
    </section>

export default ContentHeader