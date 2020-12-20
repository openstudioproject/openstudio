import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import Attendance from "./Attendance"
import { appOperations } from '../../duck'
import { classesAttendanceOperations } from './duck'
import { classesClassesOperations } from "../classes/duck"
import { customersListOperations } from '../../customers/list/duck'
import { customersSchoolInfoOperations } from '../../customers/school_info/duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        attendance: state.classes.attendance,
        barcode_scans: state.app.settings.data.customers_barcodes,
        classes: state.classes.classes,
        customers: state.customers.list,
    })

const mapDispatchToProps = dispatch =>
    ({
        fetchClassAttendance(clsID) {
            dispatch(classesAttendanceOperations.fetchClassAttendance(clsID))
        },
        updateClassAttendanceBookingStatus(clattID, status) {
            dispatch(classesAttendanceOperations.updateClassAttendanceBookingStatus(clattID, status))
        },
        deleteClassAttendance(clattID, cuID) {
            dispatch(classesAttendanceOperations.deleteClassAttendance(clattID, cuID))
        },
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        setPageSubtitle(subtitle) {
            dispatch(appOperations.setPageSubtitle(subtitle))
        },
        fetchClasses(obj) {
            dispatch(classesClassesOperations.fetchClasses(obj))
        },
        setDisplayCustomerID(cuID) {
            dispatch(customersListOperations.setDisplayCustomerID(cuID))
        },
        clearNotes() {
            dispatch(customersListOperations.clearNotes())
        },
        fetchNotes(cuID) {
            dispatch(customersListOperations.fetchNotes(cuID))
        },
        clearCustomerSchoolInfo() {
            dispatch(customersSchoolInfoOperations.clearSchoolInfo())
        },
        fetchCustomerSchoolInfo(cuID) {
            dispatch(customersSchoolInfoOperations.fetchSchoolInfo(cuID))
        }
        // clearSearchTimeout() {
        //     dispatch(classesAttendanceOperations.clearclassesAttendanceSearchTimeout())
        // },
        // setSearchTimeout(timeout) {
        //     dispatch(classesAttendanceOperations.setclassesAttendanceSearchTimeout(timeout))
        // },
        // clearSearchCustomerID() {
        //     dispatch(classesAttendanceOperations.clearclassesAttendanceSearchCustomerID())
        // },
        // setSearchCustomerID(id) {
        //     dispatch(classesAttendanceOperations.setclassesAttendanceSearchCustomerID(id))
        // },
        // clearSearchValue() {
        //     dispatch(classesAttendanceOperations.clearclassesAttendanceSearchValue())
        // },
        // setSearchValue(value) {
        //     dispatch(classesAttendanceOperations.setclassesAttendanceSearchValue(value))
        // },
    })


const AttendanceContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Attendance)))

export default AttendanceContainer