import {
    requestExpenses,
    receiveExpenses
} from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here
// const setCheckinClassAttendanceSearchCustomerID = set_customer_id

// data fetchers
const fetchExpenses = () => {
      return dispatch => {
          dispatch(requestExpenses())

          axios_os.get(OS_API.EXPENSESS)
          .then(function (response) {
            // handle success
            dispatch(receiveExpenses(response.data))
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

// helpers
const formDataToObject = (fd_obj) => {
    const data_object = {}

    for (var p of fd_obj) {
        console.log(p)
        data_object[p[0]] = p[1]
    }

    return data_object
}

// creators
const createCustomer = (data) => {
    return dispatch => {
        dispatch(requestCreateCustomer(formDataToObject(data)))

        axios_os.post(OS_API.CUSTOMER_CREATE, data)
        .then(function(response) {
            console.log(response)
            dispatch(receiveCreateCustomer(response.data))
        })
        .catch(function (error) {
            console.log(error)
        })
        .then(function() {
            //always executed
        })
    }
}

// updaters
const updateCustomer = (data) => {
    return dispatch => {
        dispatch(requestUpdateCustomer(formDataToObject(data)))

        axios_os.post(OS_API.CUSTOMER_UPDATE, data)
        .then(function(response) {
            dispatch(receiveUpdateCustomer(response.data))
        })
        .catch(function (error) {
            console.log(error)
        })
        .then(function() {
            //always executed
        })
    }
}



export default {
    // createCustomer,
    // clearCreateCustomerErrorData,
    // clearUpdateCustomerErrorData,
    // updateCustomer,
    // updateCustomerPicture,
    fetchExpenses,
}