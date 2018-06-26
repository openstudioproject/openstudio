import React, { Component } from "react"
import { render } from "react-dom"

const NavbarHeader = ({children}) =>
    <div className="navbar-header">
        <span className="navbar-brand"><b>Open</b>Studio</span>
        <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapse">
            <i className="fa fa-bars"></i>
        </button>
    </div>

export default NavbarHeader