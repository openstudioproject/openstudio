import {
    requestClassesClassAttendance as request_class_attendance,
    receiveClassesClassAttendance as receive_class_attendance,
    requestClassesClassAttendanceUpdateStatus,
    receiveClassesClassAttendanceUpdateStatus,
    requestClassesClassAttendanceDelete,
    receiveClassesClassAttendanceDelete,
    setClassesAttendanceSearchCustomerID,
    clearClassesAttendanceSearchCustomerID,
    setClassesAttendanceSearchValue,
    clearClassesAttendanceSearchValue,
    setClassesAttendanceSearchTimeout,
    clearClassesAttendanceSearchTimeout
  } from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'
import { toISODate } from '../../../../utils/date_tools'

import { customersClasscardsOperations } from '../../../customers/classcards/duck'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here

// updaters
const updateClassAttendanceBookingStatus = (clattID, status) => {
      return dispatch => {
          dispatch(requestClassesClassAttendanceUpdateStatus(clattID))

          // const date = new Date()
          // const iso_date = toISODate(date)
          const params = new URLSearchParams()
          params.append('id', clattID)
          params.append('status', status)
          console.log(params)
          axios_os.post(OS_API.CLASSES_ATTENDANCE_UPDATE, params)
          .then(function (response) {
            // handle success
            dispatch(receiveClassesClassAttendanceUpdateStatus(response.data))
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

const deleteClassAttendance = (clattID) => {
      return dispatch => {
          dispatch(requestClassesClassAttendanceDelete(clattID))

          // const date = new Date()
          // const iso_date = toISODate(date)
          const params = new URLSearchParams()
          params.append('id', clattID)
          console.log(params)
          axios_os.post(OS_API.CLASSES_ATTENDANCE_DELETE, params)
          .then(function (response) {
            // handle success
            dispatch(customersClasscardsOperations.fetchClasscards())
            dispatch(receiveClassesClassAttendanceDelete(response.data)) 
            // Refetch classcards to update count of classes taken (Server side processing only)
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
          axios_os.post(OS_API.CLASSES_ATTENDANCE, params)
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
    deleteClassAttendance,
    updateClassAttendanceBookingStatus,
    setClassesAttendanceSearchCustomerID,
    clearClassesAttendanceSearchCustomerID,
    setClassesAttendanceSearchTimeout,
    clearClassesAttendanceSearchTimeout,
    setClassesAttendanceSearchValue,
    clearClassesAttendanceSearchValue,
}
