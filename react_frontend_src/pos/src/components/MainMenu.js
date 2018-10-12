import React, { Component } from "react"
import { NavLink, withRouter } from 'react-router-dom'

import Header from "./ui/Header"
import Navbar from "./ui/Navbar"
import NavbarNav from "./ui/NavbarNav";
import NavbarHeader from "./ui/NavbarHeader"
import NavbarCollapse from "./ui/NavbarCollapse";
import NavbarCustomMenu from "./ui/NavbarCustomMenu";
import ConnectedNavbarNavUserMenu from "./ui/ConnectedNavbarNavUserMenu";

const activeClassName = 'active'


class MainMenu extends Component {
    getNavLinkClass = (path) => {
        let location = this.props.location.pathname.substring(0, path.length)
        // console.log('mm location')        
        // console.log(location)

        return ((location == path) && (path != '/')) || (path == this.props.location.pathname) ? 'active' : '';
    }

    render() {
     return (
        <Header>
        <Navbar>
            <NavbarHeader />
            <NavbarCollapse>
                <NavbarNav>
                    <li className={this.getNavLinkClass('/')}><NavLink to="/" activeClassName={activeClassName}>Home</NavLink></li>
                    <li className={this.getNavLinkClass('/checkin')}><NavLink to="/checkin" activeClassName={activeClassName}>Check-in</NavLink></li>
                    <li className={this.getNavLinkClass('/shop/products')}><NavLink to="/shop/products" activeClassName={activeClassName}>Shop</NavLink></li>
                </NavbarNav>                
            </NavbarCollapse>
            <NavbarCustomMenu>
                <ConnectedNavbarNavUserMenu />
            </NavbarCustomMenu>
        </Navbar>
        </Header>


     )}
   }

   MainMenu = withRouter(MainMenu)


export default MainMenu