import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import ButtonBack from "../../../components/ui/ButtonBack"
import PageTemplate from "../../../components/PageTemplate"
import BookOptionsList from "./BookOptionsList"



class Book extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        fetchBookingOptions: PropTypes.function,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        options: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.checkin.page_title' })
        )

        console.log(this.props.match.params.clsID)
        console.log(this.props.match.params.cuID)
        this.props.fetchBookingOptions(this.props.match.params.clsID, this.props.match.params.cuID )
    }

    onClickButtonBack() {
        this.props.history.push(`/checkin/attendance/${this.props.match.params.clsID}`)
    }

    onClickBookOption(option) {
        console.log('click book option')
        console.log(option)
    }

    render() {
        const booking_options = this.props.options.data
        

        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!this.props.options.loaded) ? 
                        <div>Loading booking options, please wait...</div> :
                        <section className="checkin_attendance">
                            <ButtonBack onClick={this.onClickButtonBack.bind(this)} 
                                        classAdditional="btn-margin-right">
                                Attendance
                            </ButtonBack>
                            <BookOptionsList booking_options={booking_options}
                                             onClick={this.onClickBookOption.bind(this)} />
                            {/* <AttendanceList attendance_items={this.props.attendance.data} /> */}
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default Book
