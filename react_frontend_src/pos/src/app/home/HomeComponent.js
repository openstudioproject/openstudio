import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import PageTemplate from "../../components/PageTemplate"


class homeComponent extends Component {
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
            this.props.intl.formatMessage({ id: 'app.pos.home.page_title' })
        )
    }

    render() {
        return (
            <PageTemplate app_state={this.props.app}>
                <section className="Welcome">
                    {/* <div>{this.props.app.loading}</div>
                    <div>{this.props.app.loading_message}</div> */}
                    {this.props.intl.formatMessage({ id: 'app.pos.home.hello' })}
                </section>
            </PageTemplate>
        )
    }
}

export default homeComponent
