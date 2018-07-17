import React, { Component } from "react"
import { render } from "react-dom"

const NavbarNav = ({children}) =>
    <ul className="nav navbar-nav">
        {children}
    </ul>

export default NavbarNav