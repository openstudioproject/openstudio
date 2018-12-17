import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'
import validator from 'validator'


import PageTemplate from "../../../components/PageTemplate"
import InputGroupSearch from "../../../components/ui/InputGroupSearch"
import ButtonBack from "../../../components/ui/ButtonBack"

import AttendanceList from "./AttendanceList"


class Attendance extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        fetchClassAttendance: PropTypes.function,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        attendance: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.checkin.page_title' })
        )

        console.log(this.props.match.params.clsID)
        this.props.fetchClassAttendance(this.props.match.params.clsID)

    }

    componentDidMount() {

    }

    // toBookingOptions(clsID, value, history) {
    //     if (isInt(value)) {
    //         history.push('/checkin/book/' + clsID + '/' + value)
    //     }
    //     console.log(value)
    //     console.log(isInt(value))
    // }

    onChange(e) {
        const value = e.target.value
        const attendance = this.props.attendance

        this.props.setSearchValue(value)

        console.log("timeout: " + attendance.searchTimeout)
        if ( attendance.searchTimeout ) {
            this.props.clearSearchTimeout()
            console.log('reset timeout')
        }

        let timeout
        this.props.setSearchTimeout(
            setTimeout(() => this.props.setSearchValue(value), 
                (validator.isInt(value)) ? timeout = 225 : timeout = 750)
        )
        // const value = e.target.value
        // const state = this.props.attendance
        // console.log("timeout: " + state.searchTimeout)
        // if ( state.searchTimeout ) {
        //     this.props.clearCheckinSearchTimeout()
        //     console.log('reset timeout')
        // }

        // const history = this.props.history
        // const clsID = this.props.match.params.clsID
        // let timeout
        // this.props.setCheckinSearchTimeout(
        //     setTimeout(() => this.toBookingOptions(clsID, value, history), 
        //         (isInt(value)) ? timeout = 225 : timeout = 750)
        // )
    }

    onClickVerifyTeacherPayment() {
        console.log('clicked verify teacher')
        this.props.history.push("/checkin/revenue/" + this.props.match.params.clsID)
    }

    onClickButtonBack() {
        console.log('button back clicked')
        this.props.history.push("/checkin")
    }
    
    render() {
        const customers = this.props.customers
        const intl = this.props.intl
        const memberships = this.props.memberships

        // let customers_display = []
        // if (customers.loaded) {
        //     if ( customers.searchID ) {
        //         customers_display = [
        //             customers.data[customers.searchID]
        //         ]
        //     } else if (customers.search_value && customers.search_value.length > 1) {
        //     Object.keys(customers.data).map( (key) => {
        //             // console.log('customer:')
        //             // console.log(key)
        //             // console.log(customers.data[key])
        //             if (customers.data[key].search_name.includes(customers.search_value)) {
        //                 customers_display.push(customers.data[key])
        //             }
        //         })
        //     }
        // }

        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!this.props.attendance.loaded) ? 
                        <div>Loading attendance, please wait...</div> :
                        <section className="checkin_attendance">
                            <div className="pull-right">
                                <button className='btn btn-default'
                                        onClick={this.onClickVerifyTeacherPayment.bind(this)} >
                                    <i className="fa fa-graduation-cap"></i> { ' ' }
                                    {this.props.intl.formatMessage({ id: "app.pos.checkin.attendane.verify_teacher_payment"})}
                                </button>
                            </div>
                            <ButtonBack onClick={this.onClickButtonBack.bind(this)} 
                                        classAdditional="pull-left btn-margin-right">
                                    Back
                                </ButtonBack>
                            <InputGroupSearch placeholder={this.props.intl.formatMessage({ id: 'app.general.placeholders.search' })}
                                              onChange={this.onChange.bind(this)} /> 
                            <AttendanceList attendance_items={this.props.attendance.data} />
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default Attendance
