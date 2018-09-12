import {
    requestShopSchoolSubscriptions as request_subscriptions,
    receiveShopSchoolSubscriptions as receive_subscriptions,
} from './actions'

import axios_os from '../../../../../utils/axios_os'
import OS_API from '../../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here

// data fetchers
const fetchShopSubscriptions = () => {
      return dispatch => {
          dispatch(request_subscriptions())

          axios_os.get(OS_API.SHOP_SCHOOL_SUBSCRIPTIONS)
          .then(function (response) {
            // handle success
            dispatch(receive_subscriptions(response.data))
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
    fetchShopSubscriptions
}
