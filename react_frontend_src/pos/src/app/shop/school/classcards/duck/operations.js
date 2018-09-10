import {
    requestShopSchoolClasscards as request_classcards,
    receiveShopSchoolClasscards as receive_classcards,
} from './actions'

import axios_os from '../../../../../utils/axios_os'
import OS_API from '../../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here

// data fetchers
const fetchShopClasscards = () => {
      return dispatch => {
          dispatch(request_classclasscards())

          axios_os.get(OS_API.SHOP_SCHOOL_CLASSCARDS)
          .then(function (response) {
            // handle success
            dispatch(receive_classcards(response.data))
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
    fetchShopClasscards
}
