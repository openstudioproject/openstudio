import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import PageTemplate from "../../../components/PageTemplate"

class bookingOptionsComponent extends Component {
    constructor(props) {
        super(props)
        console.log(props)
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
    }

    render() {
        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!this.props.classes.loaded) ? 
                        <div>Loading booking options, please wait...</div> :
                        <section className="BookingOptions">
                            {/* Booking options will go here */}
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default BookingOptionsComponent
