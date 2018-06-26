import React, { Component } from "react"
import { render } from "react-dom"

const Content = ({children}) =>
    <div className="content-wrapper">
        <section className="content">
            {children}
        </section>
    </div>

export default Content