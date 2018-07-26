import React from "react"
import NavbarNav from "./NavbarNav"

const NavbarCustomMenu = ({children}) =>
    <div className="navbar-custom-menu">
        <NavbarNav>
            {children}
        </NavbarNav>
    </div>

export default NavbarCustomMenu