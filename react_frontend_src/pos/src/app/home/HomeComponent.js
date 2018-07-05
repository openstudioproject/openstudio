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

    render() {
        return (
            <PageTemplate app_state={this.props.app_state}>
            <section className="Welcome">
                <h1>Welcome page</h1>
                <div>{this.props.app_state.loading}</div>
                <div>{this.props.app_state.loading_message}</div>
                {this.props.intl.formatMessage({ id: 'app.pos.home.hello' })}
            </section>
            </PageTemplate>
        )
    }
}

export default homeComponent
