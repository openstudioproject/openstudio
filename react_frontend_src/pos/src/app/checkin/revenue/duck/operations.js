import {
    requestCheckinRevenue as request_revenue,
    receiveCheckinRevenue as receive_revenue,
} from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'
import { toISODate } from '../../../../utils/date_tools'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here

// data fetchers
const fetchRevenue = (clsID) => {
      return dispatch => {
          dispatch(request_revenue())

          const date = new Date()
          const iso_date = toISODate(date)
          const params = new URLSearchParams()
          params.append('clsID', clsID)
          params.append('date', iso_date)
          console.log(params)
          axios_os.post(OS_API.CHECKIN_REVENUE, params)
          .then(function (response) {
            // handle success
            dispatch(receive_revenue(response.data))
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
    fetchRevenue
}
