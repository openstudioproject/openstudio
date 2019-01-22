import {
    requestMemberships,
    receiveMemberships,
} from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here
// const setCheckinClassAttendanceSearchCustomerID = set_customer_id

// data fetchers
const fetchMemberships = () => {
      return dispatch => {
          dispatch(requestMemberships())

          axios_os.post(OS_API.CUSTOMERS_MEMBERSHIPS_TODAY)
          .then(function (response) {
            // handle success
            dispatch(receiveMemberships(response.data))
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
    fetchMemberships
}
