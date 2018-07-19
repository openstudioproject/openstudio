import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import Attendance from "./AttendanceComponent"
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
    })


const AttendanceContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Attendance))

export default AttendanceContainer