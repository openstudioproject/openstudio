import React, { Component } from "react"
import PageTemplate from "../../components/PageTemplate"
import { intlShape } from "react-intl"


class homeComponent extends Component {
    constructor(props) {
        super(props)
    }

    PropTypes = {
        intl: intlShape.isRequired
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.home.page_title' })
        )
    }

    render() {
        return (
            <PageTemplate app_state={this.props.app_state}>
            <section className="Welcome">
                <div>{this.props.app_state.loading}</div>
                <div>{this.props.app_state.loading_message}</div>
                {this.props.intl.formatMessage({ id: 'app.pos.home.hello' })}
            </section>
            </PageTemplate>
        )
    }
}

export default homeComponent
