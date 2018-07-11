import React from "react"

// TODO: inject intl

const NavbarUserMenu = ({username}) =>
    <li className="dropdown user user-menu">
        <a href="#" className="dropdown-toggle" data-toggle="dropdown">
            <img src="../../dist/img/user2-160x160.jpg" className="user-image" alt="User Image"/>
            <span className="hidden-xs">{username}</span>
        </a>
        <ul className="dropdown-menu">
            <li className="user-header">
                <img src="../../dist/img/user2-160x160.jpg" className="img-circle" alt="User Image"/>
                <p>
                    {username}
                    <small></small>
                </p>
            </li>
            <li className="user-body">
                {/* TODO: add change password link */}
                <div className="row">
                    <a href="/user/change_password?_next=%2Fpos"><i class="fa fa-unlock-alt"></i> Change password</a>
                </div>
            </li>
            <li className="user-footer">
                <div className="pull-left">
                    {/* TODO: add url */}
                    <a href="#" className="btn btn-default btn-flat">Profile</a>
                </div>
                <div className="pull-right">
                    {/* TODO: add url */}
                    <a href="#" className="btn btn-default btn-flat">Sign out</a>
                </div>
        </li>
        </ul>
    </li>

export default NavbarUserMenu