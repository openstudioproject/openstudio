import React, { Component } from "react"
import { NavLink, withRouter } from 'react-router-dom'


class NavTabs extends Component {
    getNavLinkClass = (path) => {
        console.log(path)
        console.log(this.props.location.pathname)
        return (this.props.location.pathname === path) ? 'active' : '';
    }

    render() {
     return (
         <ul className="nav nav-tabs nav-justified">
            <li className={this.getNavLinkClass("/products/school/classcards")} role="presetation">
                <NavLink to="/products/school/classcards" activeClassName={activeClassName}>Classcards</NavLink>
            </li>
            <li className={this.getNavLinkClass("/products/school/subscriptions")} role="presetation">
                <NavLink to="/products/school/subscriptions" activeClassName={activeClassName}>Subscriptions</NavLink>
            </li>
         </ul>
     )};
   }
NavTabs = withRouter(NavTabs);


const activeClassName= "active"

const SchoolMenu = ({ children }) =>
    <div role="navigation">
        <NavTabs />
        <div className="tab-content">
            {children}
        </div>
    </div>

export default SchoolMenu