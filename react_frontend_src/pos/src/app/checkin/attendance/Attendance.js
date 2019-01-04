import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'
import validator from 'validator'


import PageTemplate from "../../../components/PageTemplate"
import InputGroupSearch from "../../../components/ui/InputGroupSearch"
import ButtonBack from "../../../components/ui/ButtonBack"
import ClassNameDisplay from "../../../components/ui/ClassNameDisplay"

import AttendanceList from "./AttendanceList"

import CustomersList from "../../../components/ui/CustomersList"


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
        this.props.setPageSubtitle(
            <ClassNameDisplay classes={this.props.classes}
                              clsID={this.props.match.params.clsID} />
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

    setSearchValue(value) {
        console.log('done something :)!')
        console.log(this.props)
        this.props.clearSearchCustomerID()

        const barcode_scans = this.props.barcode_scans
        const memberships = this.props.memberships.data

        console.log(barcode_scans)
        let cuID

        if (validator.isInt(value)) {
            console.log('This is an int!')
            if (barcode_scans == 'membership_id') {
                // find customer ID
                console.log('looking for cuID in memberships')
                for (const key of Object.keys(memberships)) {
                    let m = memberships[key]
                    console.log(m)
                    if ( m['date_id'] == value) {
                        cuID = m['auth_customer_id']
                    }

                }
            } else {
                cuID = value
            }

            // this.props.setDisplayCustomerID(cuID)
            this.props.setSearchCustomerID(cuID)

            console.log('customerID')
            console.log(cuID)

        } else {
            console.log('not an int value')

        }

        console.log(value)
    }

    onChangeSearch(e) {
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
            setTimeout(() => this.setSearchValue(value), 
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

    onClearSearch(e) {
        this.props.clearSearchValue()
        this.props.clearSearchCustomerID()
    }

    onClickVerifyTeacherPayment() {
        console.log('clicked verify teacher')
        this.props.history.push("/checkin/revenue/" + this.props.match.params.clsID)
    }

    onClickButtonBack() {
        console.log('button back clicked')
        this.props.history.push("/checkin")
    }

    onClickCustomersListItem(id) {
        console.log('list item clicked')
        console.log(id)
        let clsID = this.props.match.params.clsID
        this.props.history.push(`/checkin/book/${clsID}/${id}`)
    }

    onClickAttendanceButtonCheckIn(clattID) {
        console.log('Check in clicked')
        console.log(clattID)
        
        this.props.updateClassAttendanceBookingStatus(clattID, "attending")
    }
    
    render() {
        const attendance = this.props.attendance
        const customers = this.props.customers
        const intl = this.props.intl
        const memberships = this.props.memberships

        let customers_display = []
        if (customers.loaded) {
            if ( attendance.searchCustomerID ) {
                customers_display = [
                    customers.data[attendance.searchCustomerID]
                ]
            } else if (attendance.searchValue && attendance.searchValue.length > 1) {
            Object.keys(customers.data).map( (key) => {
                    // console.log('customer:')
                    // console.log(key)
                    // console.log(customers.data[key])
                    if (customers.data[key].search_name.includes(attendance.searchValue)) {
                        customers_display.push(customers.data[key])
                    }
                })
            }
        }

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
                                Classes
                            </ButtonBack>
                            <InputGroupSearch placeholder={this.props.intl.formatMessage({ id: 'app.general.placeholders.search' })}
                                              onChange={this.onChangeSearch.bind(this)}
                                              onClear={this.onClearSearch.bind(this)}
                                              value={attendance.searchValue} /> 
                            { (attendance.searchCustomerID || attendance.searchValue) ?
                                <CustomersList customers={customers_display}
                                            title="Add customers"
                                            intl={intl}
                                            onClick={this.onClickCustomersListItem.bind(this)} />
                                : ''
                            }
                            <AttendanceList attendance_items={this.props.attendance.data}
                                            intl={intl}
                                            title="Attendance"
                                            onClickCheckIn={this.onClickAttendanceButtonCheckIn.bind(this)} />
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default Attendance
