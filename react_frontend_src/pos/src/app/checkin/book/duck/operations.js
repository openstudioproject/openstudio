import {
    requestCheckinClassAttendance as request_class_attendance,
    receiveCheckinClassAttendance as receive_class_attendance,
    setCheckinClassAttendanceLoading as set_loading
} from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here


// data fetchers
const fetchClassAttendance = (clsID) => {
      return dispatch => {
          dispatch(request_class_attendance())

          console.log("fetch class attendance")
          console.log(clsID)
          const params = new URLSearchParams()
          params.append('clsID', clsID)
          console.log(params)
          axios_os.post(OS_API.CHECKIN_ATTENDANCE, params)
          .then(function (response) {
            // handle success
            dispatch(receive_class_attendance(response.data))
            // dispatch(setLoadingProgress(100))
          })
          .catch(function (error) {
            // handle error
            console.log(error)
          })
          .then(function () {
            // always executed
          });
      }
  }


export default {
    fetchClassAttendance
}
