import {
    requestSubscriptions,
    receiveSubscriptions,
} from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here

// data fetchers
const fetchSubscriptions = () => {
      return dispatch => {
          dispatch(requestSubscriptions())

          axios_os.post(OS_API.CUSTOMERS_SUBSCRIPTIONS)
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
