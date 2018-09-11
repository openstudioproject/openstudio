import React from "react"
import { NavLink } from 'react-router-dom'

import Header from "./ui/Header"
import Navbar from "./ui/Navbar"
import NavbarNav from "./ui/NavbarNav";
import NavbarHeader from "./ui/NavbarHeader"
import NavbarCollapse from "./ui/NavbarCollapse";
import NavbarCustomMenu from "./ui/NavbarCustomMenu";
import ConnectedNavbarNavUserMenu from "./ui/ConnectedNavbarNavUserMenu";

const activeClassName= "active"

const MainMenu = () =>
    <Header>
        <Navbar>
            <NavbarHeader />
            <NavbarCollapse>
                <NavbarNav>
                    <li><NavLink to="/" activeClassName={activeClassName}>Home</NavLink></li>
                    <li><NavLink to="/checkin" activeClassName={activeClassName}>Check-in</NavLink></li>
                    <li><NavLink to="/products/school/classcards" activeClassName={activeClassName}>Point of Sale</NavLink></li>
                </NavbarNav>                
            </NavbarCollapse>
            <NavbarCustomMenu>
                <ConnectedNavbarNavUserMenu />
            </NavbarCustomMenu>
        </Navbar>
    </Header>

export default MainMenu