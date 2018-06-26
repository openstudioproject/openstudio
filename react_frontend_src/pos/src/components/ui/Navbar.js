import React, { Component } from "react"
import { render } from "react-dom"

const Navbar = ({children}) =>
    <nav className="navbar navbar-static-top">
        {children}
    </nav>

export default Navbar