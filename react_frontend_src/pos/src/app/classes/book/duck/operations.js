import { withRouter } from 'react-router'

import {
    requestClassesBookingOptions as request_booking_options,
    receiveClassesBookingOptions as receive_booking_options,
    requestClassesCustomer,
    receiveClassesCustomer
} from './actions'

import { toast } from 'react-toastify'

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
          axios_os.post(OS_API.CLASSES_BOOKING_OPTIONS, params)
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

const classesCustomer = (cuID, clsID, data, history) => {
      return dispatch => {
          dispatch(requestClassesCustomer())

          console.log("request customer classes")
          let fd = new FormData()
        //   fd.append('clsID', clsID)
          fd.append('cuID', cuID)
          // Add data items
          Object.keys(data).map((key) =>
            fd.append(key, data[key])
          )
  
          axios_os.post(OS_API.CLASSES_BOOKING_CREATE, fd)
          .then(function(response) {
              dispatch(receiveClassesCustomer(response.data))
              if (!response.data.error) {
                  history.push(`/classes/attendance/${clsID}`)
              } else {
                toast.info("Customer is already checked-in to this class", {
                  position: toast.POSITION.BOTTOM_RIGHT
                });
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
    classesCustomer,
    fetchBookingOptions
}
