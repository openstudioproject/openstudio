import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import Attendance from "./Attendance"
import { appOperations } from '../../duck'
import { checkinAttendanceOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        attendance: state.checkin.attendance,
        barcode_scans: state.app.settings.data.customers_barcodes,
        classes: state.checkin.classes.data,
        customers: state.customers.list,
        memberships: state.customers.memberships
    })

const mapDispatchToProps = dispatch =>
    ({
        fetchClassAttendance(clsID) {
            dispatch(checkinAttendanceOperations.fetchClassAttendance(clsID))
        },
        updateClassAttendanceBookingStatus(clattID, status) {
            dispatch(checkinAttendanceOperations.updateClassAttendanceBookingStatus(clattID, status))
        },
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        setPageSubtitle(subtitle) {
            dispatch(appOperations.setPageSubtitle(subtitle))
        },
        clearSearchTimeout() {
            dispatch(checkinAttendanceOperations.clearCheckinAttendanceSearchTimeout())
        },
        setSearchTimeout(timeout) {
            dispatch(checkinAttendanceOperations.setCheckinAttendanceSearchTimeout(timeout))
        },
        clearSearchCustomerID() {
            dispatch(checkinAttendanceOperations.clearCheckinAttendanceSearchCustomerID())
        },
        setSearchCustomerID(id) {
            dispatch(checkinAttendanceOperations.setCheckinAttendanceSearchCustomerID(id))
        },
        clearSearchValue() {
            dispatch(checkinAttendanceOperations.clearCheckinAttendanceSearchValue())
        },
        setSearchValue(value) {
            dispatch(checkinAttendanceOperations.setCheckinAttendanceSearchValue(value))
        },
    })


const AttendanceContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Attendance)))

export default AttendanceContainer