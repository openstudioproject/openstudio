import React, { Component } from "react"
import { NavLink, withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl';

class NavTabs extends Component {
    getNavLinkClass = (path) => {
        // console.log(path)
        // console.log(this.props.location.pathname)
        return (this.props.location.pathname === path) ? 'active' : '';
    }

    render() {
        const intl = this.props.intl

        return (
            <ul className="nav nav-tabs nav-justified">
                <li className={this.getNavLinkClass("/shop/school/classcards")} role="presetation">
                    <NavLink to="/shop/school/classcards" activeClassName={activeClassName}>
                        {intl.formatMessage({ id:"app.general.strings.classcards" })}
                    </NavLink>
                </li>
                <li className={this.getNavLinkClass("/shop/school/subscriptions")} role="presetation">
                    <NavLink to="/shop/school/subscriptions" activeClassName={activeClassName}>
                        {intl.formatMessage({ id:"app.general.strings.subscriptions" })}
                    </NavLink>
                </li>
                <li className={this.getNavLinkClass("/shop/school/memberships")} role="presetation">
                    <NavLink to="/shop/school/memberships" activeClassName={activeClassName}>
                        {intl.formatMessage({ id:"app.general.strings.memberships" })}
                    </NavLink>
                </li>
            </ul>
         )};
   }
NavTabs = injectIntl(withRouter(NavTabs));


const activeClassName= "active"

const SchoolMenu = ({ children }) =>
    <div role="navigation">
        <NavTabs />
        <div className="tab-content">
            {children}
        </div>
    </div>

export default SchoolMenu