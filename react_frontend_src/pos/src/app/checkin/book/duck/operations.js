import { withRouter } from 'react-router'

import {
    requestCheckinBookingOptions as request_booking_options,
    receiveCheckinBookingOptions as receive_booking_options,
    requestCheckinCustomer,
    receiveCheckinCustomer
} from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here


// data fetchers
const fetchBookingOptions = (clsID, cuID) => {
      return dispatch => {
          dispatch(request_booking_options())

          console.log("fetch booking options")
          console.log(clsID)
          console.log(cuID)
          const params = new URLSearchParams()
          params.append('clsID', clsID)
          params.append('cuID', cuID)
          console.log(params)
          axios_os.post(OS_API.CHECKIN_BOOKING_OPTIONS, params)
          .then(function (response) {
            // handle success
            dispatch(receive_booking_options(response.data))
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

const checkinCustomer = (cuID, clsID, data, history) => {
      return dispatch => {
          dispatch(requestCheckinCustomer())

          console.log("request customer checkin")
          let fd = new FormData()
        //   fd.append('clsID', clsID)
          fd.append('cuID', cuID)
          // Add data items
          Object.keys(data).map((key) =>
            fd.append(key, data[key])
          )
  
          axios_os.post(OS_API.CHECKIN_BOOKING_CREATE, fd)
          .then(function(response) {
              dispatch(receiveCheckinCustomer(response.data))
              if (!response.data.error) {
                  history.push(`/checkin/attendance/${clsID}`)
              }
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
    checkinCustomer,
    fetchBookingOptions
}
