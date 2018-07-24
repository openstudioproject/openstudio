import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import PageTemplate from "../../../components/PageTemplate"

import AttendanceList from "./AttendanceList"


const InputGroupSearch = ({placeholder, onChange=f=>f}) => 
    <div className="input-group">
        <span className="input-group-addon">
            <i className="fa fa-search"></i>
        </span>
        <input type="text"
               className="form-control"
               placeholder={placeholder} 
               onChange={onChange}
               ref={input => input && input.focus()} />
            {/* placeholder="Search..." /> */}
    </div>


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

    // state = {
    //     typingTimeout: 0
    // }

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
        // // this.props.setCheckinSearchTimeout(
        // this.setState({
        //     typingTimeout: setTimeout(() => this.toBookingOptions(clsID, value, history), 1000)
        // })
    }
    // onChange(e) {
    //     const value = e.target.value
    //     const state = this.props.attendance
    //     console.log(this.state.typingTimeout)
    //     if ( this.state.typingTimeout ) {
    //         clearTimeout(this.state.typingTimeout)
    //     }

    //     const history = this.props.history
    //     const clsID = this.props.match.params.clsID
    //     // this.props.setCheckinSearchTimeout(
    //     this.setState({
    //         typingTimeout: setTimeout(() => this.toBookingOptions(clsID, value, history), 1000)
    //     })
    // }


    
    render() {
        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!this.props.attendance.loaded) ? 
                        <div>Loading attendance, please wait...</div> :
                        <section className="checkin_attendance">
                            <InputGroupSearch placeholder={this.props.intl.formatMessage({ id: 'app.general.placeholders.search' })}
                                              onChange={this.onChange.bind(this)} /> <br />
                            <AttendanceList attendance_items={this.props.attendance.data} />
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default Attendance
