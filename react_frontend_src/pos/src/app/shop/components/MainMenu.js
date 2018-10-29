import React, { Component } from "react"
import { NavLink, withRouter } from 'react-router-dom'



class NavTabs extends Component {
    getNavLinkClass = (path) => {
        // console.log('pathname')
        // console.log(this.props.location.pathname)
        // console.log('path')
        // console.log(path)      

        return !(this.props.location.pathname.search(path)) ? 'active' : '';
    }

    render() {
     return (
         <ul className="nav nav-tabs">
            <li className={this.getNavLinkClass("/shop/products")} role="presetation">
                <NavLink to="/shop/products" activeClassName={activeClassName}>Products</NavLink>
            </li>
            <li className={this.getNavLinkClass("/shop/school")} role="presetation">
                <NavLink to="/shop/school/classcards" activeClassName={activeClassName}>School</NavLink>
            </li>
         </ul>
     )}
   }
NavTabs = withRouter(NavTabs);


const activeClassName= "active"

const ShopMainMenu = ({ children }) =>
    <div className="nav-tabs-custom">
        <NavTabs />
        <div className="tab-content">
            {children}
        </div>
    </div>

export default ShopMainMenu