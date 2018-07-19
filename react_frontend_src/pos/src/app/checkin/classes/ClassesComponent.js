import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import PageTemplate from "../../../components/PageTemplate"
import ClassesList from "./ClassesListComponent"

class classesComponent extends Component {
    constructor(props) {
        super(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        fetchClasses: PropTypes.function,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        classes: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.checkin.page_title' })
        )
        this.props.fetchClasses()
    }

    render() {
        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!this.props.classes.loaded) ? 
                        <div>Loading classes, please wait...</div> :
                        <section className="checkin_classes">
                            <ClassesList classes={this.props.classes.data} />
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default classesComponent
