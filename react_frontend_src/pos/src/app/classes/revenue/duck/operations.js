import {
    requestClassesRevenue as request_revenue,
    receiveClassesRevenue as receive_revenue,
    requestClassesTeacherPayment as request_teacher_payment,
    receiveClassesTeacherPayment as receive_teacher_payment,
    requestClassesVerifyTeacherPayment as request_verify_payment,
    receiveClassesVerifyTeacherPayment as receive_verify_payment,
} from './actions'

import axios from 'axios'
import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'
import { toISODate } from '../../../../utils/date_tools'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here

// data fetchers
function getRevenue(clsID) {
  const date = new Date()
  const iso_date = toISODate(date)
  const params = new URLSearchParams()
  params.append('clsID', clsID)
  params.append('date', iso_date)
  console.log(params)
  return axios_os.post(OS_API.CLASSES_REVENUE, params)
}

function getTeacherPayment(clsID) {
  const date = new Date()
  const iso_date = toISODate(date)
  const params = new URLSearchParams()
  params.append('clsID', clsID)
  params.append('date', iso_date)
  console.log(params)
  return axios_os.post(OS_API.CLASSES_TEACHER_PAYMENT, params)
}

const fetchRevenue = (clsID) => {
      return dispatch => {
          dispatch(request_revenue())

          getRevenue(clsID)
          .then(function (response) {
            // handle success
            dispatch(receive_revenue(response.data))
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

const fetchTeacherPayment = (clsID) => {
      return dispatch => {
          dispatch(request_teacher_payment())

          getTeacherPayment(clsID)
          .then(function (response) {
            // handle success
            dispatch(receive_teacher_payment(response.data))
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

const fetchRevenueAndTeacherPayment = (clsID) => { 
  return dispatch => {
    dispatch(request_revenue())
    dispatch(request_teacher_payment())

    axios.all([getRevenue(clsID), getTeacherPayment(clsID)])
      .then(axios.spread(function (revenue, teacher_payment) {
        // Both requests are now complete
        dispatch(receive_revenue(revenue.data))
        dispatch(receive_teacher_payment(teacher_payment.data))
        
      })
    );
  }
}

const verifyTeacherPayment = (tpcID) => {
  return dispatch => {
    dispatch(request_verify_payment())

    const params = new URLSearchParams()
    params.append('tpcID', tpcID)
    console.log(params)
    axios_os.post(OS_API.CLASSES_VERIFY_TEACHER_PAYMENT, params)
    .then(function (response) {
      // handle success
      dispatch(receive_verify_payment(response.data))
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
    fetchRevenue,
    fetchTeacherPayment,
    fetchRevenueAndTeacherPayment,
    verifyTeacherPayment
}
