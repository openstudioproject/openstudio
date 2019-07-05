import {
    requestSubscriptions,
    receiveSubscriptions,
} from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here

// data fetchers
const fetchSubscriptions = (id) => {
      return dispatch => {
          dispatch(requestSubscriptions())

          let fd = new FormData()
          fd.append('id', id)

          axios_os.post(OS_API.CUSTOMER_SUBSCRIPTIONS, fd)
          .then(function (response) {
            // handle success
            dispatch(receiveSubscriptions(response.data))
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
    fetchSubscriptions
}
