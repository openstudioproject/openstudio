import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import PageTemplate from "../../components/PageTemplate"


class classesComponent extends Component {
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
            this.props.intl.formatMessage({ id: 'app.pos.checkin.page_title' })
        )
    }

    render() {
        return (
            <PageTemplate app_state={this.props.app}>
                <section className="ClassesList">
                    Hello world from the classes component
                </section>
            </PageTemplate>
        )
    }
}

export default classesComponent
