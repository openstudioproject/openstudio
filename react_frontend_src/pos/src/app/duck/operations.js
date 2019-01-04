import {
    requestPaymentMethods,
    receivePaymentMethods,
    requestValidateCart,
    receiveValidateCart,
    requestUser as request_user,
    receiveUser as receive_user,
    requestSettings as request_settings,
    receiveSettings as receive_settings,
    setError as set_error,
    setErrorMessage as set_error_message,
    setErrorData as set_error_data,
    setLoaded as set_loaded,
    setLoading as set_loading,
    setLoadingMessage as set_loading_message,
    setLoadingProgress as set_loading_progress,
    setPageTitle,
    setPageSubtitle,
    clearPageSubtitle
} from './actions'

import axios_os from '../../utils/axios_os'
import OS_API from '../../utils/os_api'

// just pass these actions as there's nothing else they need to do
const setError = set_error
const setErrorMessage = set_error_message
const setErrorData = set_error_data
const setLoadingMessage = set_loading_message
const setLoadingProgress = set_loading_progress
const setLoaded = set_loaded
const setLoading = set_loading


// data fetchers

const fetchPaymentMethods = () => {
  return dispatch => {
      dispatch(requestPaymentMethods)
      dispatch(setLoading())

      dispatch(set_loading_message("Payment methods"))
      axios_os.get(OS_API.APP_PAYMENT_METHODS)
      .then(function (response) {
        // handle success
        console.log('receive payment methods here')
        dispatch(receivePaymentMethods(response.data))
        dispatch(setLoaded())  
        dispatch(setLoading())        
      })
      .catch(function (error) {
        // handle error
        console.log(error)
        dispatch(setError(true))
        dispatch(setErrorMessage("Error loading payment methods"))
        if (error.config) {
          dispatch(setErrorData(error.config.url))
        } 
      })
      .then(function () {
        // always executed
      });
  }
}


const fetchUser = () => {
    return dispatch => {
        dispatch(request_user)
        dispatch(setLoading())

        dispatch(set_loading_message("User profile"))
        axios_os.get(OS_API.APP_USER)
        .then(function (response) {
          // handle success
          console.log('receive user here')
          dispatch(receive_user(response.data))
          dispatch(setLoaded())  
          dispatch(setLoading())        
          // dispatch(setLoadingProgress(50))
          // dispatch(setLoaded(true))
          // dispatch(setLoading(false))
        })
        .catch(function (error) {
          // handle error
          console.log(error)
          dispatch(setError(true))
          dispatch(setErrorMessage("Error loading user data"))
          if (error.config) {
            dispatch(setErrorData(error.config.url))
          } 
        })
        .then(function () {
          // always executed
        });
    }
}

const fetchSettings = () => {
    return dispatch => {
        dispatch(request_settings)
        dispatch(setLoading())

        dispatch(set_loading_message("Settings"))
        axios_os.get(OS_API.APP_SETTINGS)
        .then(function (response) {
          // handle success
          dispatch(receive_settings(response.data))
          dispatch(setLoaded())
          dispatch(setLoading())
        })
        .catch(function (error) {
          // handle error
          dispatch(setError(true))
          dispatch(setErrorMessage("Error loading settings data"))
          if (error.config) {
            dispatch(setErrorData(error.config.url))
          } 
        })
        .then(function () {
          // always executed
        });
    }
}


const validateCart = (state) => {
  return dispatch => {
    dispatch(requestValidateCart())

    // const date = new Date()
    // const iso_date = toISODate(date)
    console.log(state)
    // const params = new URLSearchParams()

    // params.append('customerID', state.customers.list.selectedID)
    // params.append('items', state.shop.cart.items)

    // params.append('clsID', clsID)
    // params.append('date', iso_date)
    // console.log(params)
    let payload = {
      payment_methodID: state.shop.payment.selectedID,
      customerID: state.customers.list.selectedID,
      items: state.shop.cart.items
    }

    axios_os.post(OS_API.APP_VALIDATE_CART, payload)
    .then(function (response) {
      // handle success
      dispatch(receiveValidateCart(response.data))
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
    fetchPaymentMethods,
    fetchUser,
    fetchSettings,
    validateCart,
    setError,
    setErrorData,
    setErrorMessage,
    setLoaded,
    setLoading,
    setLoadingMessage,
    setLoadingProgress,
    setPageTitle,
    setPageSubtitle,
    clearPageSubtitle
}
