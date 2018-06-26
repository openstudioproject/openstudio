import React, { Component } from "react"
import { render } from "react-dom"

const NavbarNav = ({children}) =>
    <ul className="nav navbar-nav">
        <li className="active"><a href="#">Link <span className="sr-only">(current)</span></a></li>
        {children}
    </ul>

export default NavbarNav