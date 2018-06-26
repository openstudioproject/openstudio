import React, { Component } from "react"
import { render } from "react-dom"

const Header = ({children}) =>
    <header className="main-header">
        {children}
    </header>

export default Header