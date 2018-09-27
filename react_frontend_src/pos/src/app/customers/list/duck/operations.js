import {
    requestCustomers,
    receiveCustomers,
    requestCreateCustomer,
    receiveCreateCustomer,
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
        dispatch(requestCreateCustomer())

        // const params = new URLSearchParams()
        // params.append('clsID', clsID)
        // params.append('date', iso_date)
        // console.log(params)
        // axios_os.post(OS_API.CHECKIN_ATTENDANCE, params)
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


export default {
    createCustomer,
    fetchCustomers,
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
}
