import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'


import PageTemplate from "../../components/PageTemplate"
import InputGroupSearch from "../../components/ui/InputGroupSearch"


class Customers extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        customers: PropTypes.object,
    }

    componentWillMount() {
        // this.props.setPageTitle(
        //     this.props.intl.formatMessage({ id: 'app.pos.checkin.page_title' })
        // )
    }

    componentDidMount() {

    }

    onChange(e) {
        console.log(e)
    }
   
    render() {
        const customers = this.props.customers

        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!customers.loaded) ? 
                        <div>Loading customers, please wait...</div> :
                        <section className="customers_main">
                            {/* <div className="pull-right">
                                <NavLink to={"/checkin/revenue/" + this.props.match.params.clsID}>
                                    {this.props.intl.formatMessage({ id: "app.pos.checkin.attendane.verify_teacher_payment"})}
                                </NavLink>
                            </div> */}
                            <InputGroupSearch placeholder={this.props.intl.formatMessage({ id: 'app.general.placeholders.search' })}
                                              onChange={this.onChange.bind(this)} /> <br />
                            {/* <AttendanceList attendance_items={this.props.attendance.data} /> */}
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default Attendance
