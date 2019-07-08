import {
    requestSchoolInfo,
    receiveSchoolInfo,
} from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here
// const setClassesClassAttendanceSearchCustomerID = set_customer_id

// data fetchers
const fetchSchoolInfo = (id) => {
      return dispatch => {
          dispatch(requestSchoolInfo())

          let fd = new FormData()
          fd.append('id', id)

          axios_os.post(OS_API.CUSTOMER_SCHOOL_INFO, fd)
          .then(function (response) {
            // handle success
            dispatch(receiveSchoolInfo(response.data))
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
    fetchSchoolInfo
}
