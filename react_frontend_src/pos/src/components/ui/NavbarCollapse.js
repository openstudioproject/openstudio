import React, { Component } from "react"
import { render } from "react-dom"

const NavbarCollapse = ({children}) =>
    <div className="collapse navbar-collapse pull-left" id="navbar-collapse">
        {children}
    </div>

export default NavbarCollapse