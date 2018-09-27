import {
    requestCustomers,
    receiveCustomers,
    // setCheckinClassAttendanceSearchCustomerID as set_customer_id,
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

          axios_os.post(OS_API.CUSTOMERS)
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


export default {
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
