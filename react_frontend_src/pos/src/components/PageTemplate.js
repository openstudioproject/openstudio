import React, { Component } from "react"
import { render } from "react-dom"

const PageTemplate = ({children}) =>
    <div className="page">
        hello world
        {children}
    </div>

export default PageTemplate