import {
    requestUser as request_user,
    receiveUser as receive_user,
    setError as set_error,
    setErrorMessage as set_error_message,
    setErrorData as set_error_data,
    setLoaded as set_loaded,
    setLoading as set_loading,
    setLoadingMessage as set_loading_message,
    setLoadingProgress as set_loading_progress,
    setPageTitle as set_page_title
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
const setPageTitle = set_page_title


// data fetchers
const fetchUser = () => {
    return dispatch => {
        dispatch(request_user)

        dispatch(set_loading_message("user profile"))
        axios_os.get(OS_API.APP_USER)
        .then(function (response) {
          // handle success
          dispatch(receive_user(response.data))
          dispatch(setLoadingProgress(100))
          dispatch(setLoaded(true))
          dispatch(setLoading(false))
        })
        .catch(function (error) {
          // handle error
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

export default {
    fetchUser,
    setError,
    setErrorData,
    setErrorMessage,
    setLoaded,
    setLoading,
    setLoadingMessage,
    setLoadingProgress,
    setPageTitle,
}
