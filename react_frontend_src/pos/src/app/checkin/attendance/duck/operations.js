import {
    requestCheckinClassAttendance as request_class_attendance,
    receiveCheckinClassAttendance as receive_class_attendance,
    requestCheckinClassAttendanceUpdateStatus,
    receiveCheckinClassAttendanceUpdateStatus,
    setCheckinAttendanceSearchCustomerID,
    clearCheckinAttendanceSearchCustomerID,
    setCheckinAttendanceSearchValue,
    clearCheckinAttendanceSearchValue,
    setCheckinAttendanceSearchTimeout,
    clearCheckinAttendanceSearchTimeout
  } from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'
import { toISODate } from '../../../../utils/date_tools'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here

// updaters
const updateClassAttendanceBookingStatus = (clattID, status) => {
      return dispatch => {
          dispatch(requestCheckinClassAttendanceUpdateStatus(clattID))

          // const date = new Date()
          // const iso_date = toISODate(date)
          const params = new URLSearchParams()
          params.append('clattID', clattID)
          params.append('status', status)
          console.log(params)
          axios_os.post(OS_API.CHECKIN_ATTENDANCE_UPDATE, params)
          .then(function (response) {
            // handle success
            dispatch(receiveCheckinClassAttendanceUpdateStatus(response.data))
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

// data fetchers
const fetchClassAttendance = (clsID) => {
      return dispatch => {
          dispatch(request_class_attendance())

          const date = new Date()
          const iso_date = toISODate(date)
          const params = new URLSearchParams()
          params.append('clsID', clsID)
          params.append('date', iso_date)
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
    fetchClassAttendance,
    updateClassAttendanceBookingStatus,
    setCheckinAttendanceSearchCustomerID,
    clearCheckinAttendanceSearchCustomerID,
    setCheckinAttendanceSearchTimeout,
    clearCheckinAttendanceSearchTimeout,
    setCheckinAttendanceSearchValue,
    clearCheckinAttendanceSearchValue,
}
