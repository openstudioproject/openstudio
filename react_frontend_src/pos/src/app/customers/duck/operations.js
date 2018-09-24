import {
    requestCustomers,
    receiveCustomers
    // setCheckinClassAttendanceSearchCustomerID as set_customer_id,
    // setCheckinSearchTimeout as set_search_timeout,
    // clearCheckinSearchTimeout as clear_search_timeout
} from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here
// const setCheckinClassAttendanceSearchCustomerID = set_customer_id
// const clearCheckinSearchTimeout = clear_search_timeout
// const setCheckinSearchTimeout = set_search_timeout

// data fetchers
const fetchCustomers = () => {
      return dispatch => {
          dispatch(requestCustomers())

          console.log(params)
          axios_os.post(OS_API.CUSTOMERS, params)
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
    fetchCustomers
    // setCheckinClassAttendanceSearchCustomerID,
    // setCheckinSearchTimeout,
    // clearCheckinSearchTimeout
}
