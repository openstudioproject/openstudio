import {
    requestCustomers,
    receiveCustomers,
    requestCreateCustomer,
    receiveCreateCustomer,
    requestUpdateCustomer,
    receiveUpdateCustomer,
    setCreateCustomerStatus,
    setUpdateCustomerStatus,
    setSearchTimeout,
    clearSearchTimeout,
    setDisplayCustomerID,
    clearDisplayCustomerID,
    setSearchCustomerID,
    clearSearchCustomerID,
    setSearchValue,
    clearSearchValue,
    setSelectedCustomerID,
    clearSelectedCustomerID
} from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here
// const setCheckinClassAttendanceSearchCustomerID = set_customer_id

// data fetchers
const fetchCustomers = () => {
      return dispatch => {
          dispatch(requestCustomers())

          axios_os.get(OS_API.CUSTOMERS)
          .then(function (response) {
            // handle success
            dispatch(receiveCustomers(response.data))
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

// creators
const createCustomer = (data) => {
    return dispatch => {
        const data_object = {}
        console.log('logging form data object stuff')

        for (var p of data) {
            console.log(p)
            data_object[p[0]] = p[1]
        }

        console.log(data_object)


        dispatch(requestCreateCustomer(data_object))

        axios_os.post(OS_API.CUSTOMER_CREATE, data)
        .then(function(response) {
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
        dispatch(requestUpdateCustomer())

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
    createCustomer,
    updateCustomer,
    fetchCustomers,
    setSearchTimeout,
    clearSearchTimeout,
    setCreateCustomerStatus,
    setUpdateCustomerStatus,
    setDisplayCustomerID,
    clearDisplayCustomerID,
    setSearchCustomerID,
    clearSearchCustomerID,
    setSearchValue,
    clearSearchValue,
    setSelectedCustomerID,
    clearSelectedCustomerID
}
