import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import Header from "../../components/ui/Header"
import Navbar from "../../components/ui/Navbar"
import NavbarHeader from "../../components/ui/NavbarHeader"
import Content from "../../components/ui/Content"


class SystemError extends Component {
    constructor(props) {
        super(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app_state: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.system_error.page_title' })
        )
    }

    render() {
        return (
            <div>
                <Header>
                    <Navbar>
                        <NavbarHeader />
                    </Navbar>
                </Header>
                <Content title={this.props.app_state.current_page_title}>
                    <section className="error">
                        {this.props.intl.formatMessage({ id: 'app.pos.system_error.content' })}
                    </section>
                </Content>
            </div>
        )
    }
}

export default SystemError
