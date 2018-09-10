import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import Attendance from "./Attendance"
import { appOperations } from '../../duck'
import { checkinAttendanceOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        attendance: state.checkin_attendance
    })

const mapDispatchToProps = dispatch =>
    ({
        fetchClassAttendance(clsID) {
            dispatch(checkinAttendanceOperations.fetchClassAttendance(clsID))
        },
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        clearCheckinSearchTimeout() {
            dispatch(checkinAttendanceOperations.clearCheckinSearchTimeout())
        },
        setCheckinSearchTimeout(timeout) {
            dispatch(checkinAttendanceOperations.setCheckinSearchTimeout(timeout))
        }
    })


const AttendanceContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Attendance)))

export default AttendanceContainer