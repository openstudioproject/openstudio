import React, { Component } from "react"

const Content = ({children}) =>
    <div className="content-wrapper">
        <section className="content">
            {children}
        </section>
    </div>

export default Content