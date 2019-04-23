import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import Attendance from "./Attendance"
import { appOperations } from '../../duck'
import { classesAttendanceOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        attendance: state.classes.attendance,
        barcode_scans: state.app.settings.data.customers_barcodes,
        classes: state.classes.classes.data,
        customers: state.customers.list,
        memberships: state.customers.memberships
    })

const mapDispatchToProps = dispatch =>
    ({
        fetchClassAttendance(clsID) {
            dispatch(classesAttendanceOperations.fetchClassAttendance(clsID))
        },
        updateClassAttendanceBookingStatus(clattID, status) {
            dispatch(classesAttendanceOperations.updateClassAttendanceBookingStatus(clattID, status))
        },
        deleteClassAttendance(clattID) {
            dispatch(classesAttendanceOperations.deleteClassAttendance(clattID))
        },
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        setPageSubtitle(subtitle) {
            dispatch(appOperations.setPageSubtitle(subtitle))
        },
        clearSearchTimeout() {
            dispatch(classesAttendanceOperations.clearclassesAttendanceSearchTimeout())
        },
        setSearchTimeout(timeout) {
            dispatch(classesAttendanceOperations.setclassesAttendanceSearchTimeout(timeout))
        },
        clearSearchCustomerID() {
            dispatch(classesAttendanceOperations.clearclassesAttendanceSearchCustomerID())
        },
        setSearchCustomerID(id) {
            dispatch(classesAttendanceOperations.setclassesAttendanceSearchCustomerID(id))
        },
        clearSearchValue() {
            dispatch(classesAttendanceOperations.clearclassesAttendanceSearchValue())
        },
        setSearchValue(value) {
            dispatch(classesAttendanceOperations.setclassesAttendanceSearchValue(value))
        },
    })


const AttendanceContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Attendance)))

export default AttendanceContainer