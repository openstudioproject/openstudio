import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { Link } from 'react-router-dom'

import PageTemplate from "../../../components/PageTemplate"
import ClassesList from "./ClassesList"

class Classes extends Component {
    constructor(props) {
        console.log(props)
        super(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        classes: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.classes.page_title' })
        )
        this.props.setPageSubtitle("")
    }

    render() {
        const customerID = this.props.match.params.customerID
        console.log('classes customerID')
        console.log(customerID)

        const back = <Link to="/" className="btn btn-default"><i className="fa fa-angle-double-left"></i> Back</Link>
        
        return (
            <PageTemplate app_state={this.props.app} tools={back}>
                { 
                    (!this.props.classes.loaded) ? 
                        <div>Loading classes, please wait...</div> :
                        <section className="classes_classes">
                            <ClassesList 
                                classes={this.props.classes.data} 
                                customerID={customerID}
                            />
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default Classes
