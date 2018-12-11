import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'


import PageTemplate from "../../../components/PageTemplate"
import InputGroupSearch from "../../../components/ui/InputGroupSearch"

import AttendanceList from "./AttendanceList"


// const InputGroupSearch = ({placeholder, onChange=f=>f}) => 
//     <div className="input-group">
//         <span className="input-group-addon">
//             <i className="fa fa-search"></i>
//         </span>
//         <input type="text"
//                className="form-control"
//                placeholder={placeholder} 
//                onChange={onChange}
//                ref={input => input && input.focus()} />
//             {/* placeholder="Search..." /> */}
//     </div>


function isInt(value) {
    return !isNaN(value) && 
           parseInt(Number(value)) == value && 
           !isNaN(parseInt(value, 10));
  }

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

    toBookingOptions(clsID, value, history) {
        if (isInt(value)) {
            history.push('/checkin/book/' + clsID + '/' + value)
        }
        console.log(value)
        console.log(isInt(value))
    }

    onChange(e) {
        const value = e.target.value
        const state = this.props.attendance
        console.log("timeout: " + state.searchTimeout)
        if ( state.searchTimeout ) {
            this.props.clearCheckinSearchTimeout()
            console.log('reset timeout')
        }

        const history = this.props.history
        const clsID = this.props.match.params.clsID
        let timeout
        this.props.setCheckinSearchTimeout(
            setTimeout(() => this.toBookingOptions(clsID, value, history), 
                (isInt(value)) ? timeout = 225 : timeout = 750)
        )
    }

    onClickVerifyTeacherPayment() {
        console.log('clicked verify teacher')
        this.props.history.push("/checkin/revenue/" + this.props.match.params.clsID)
    }
    
    render() {
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
