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

// Example:

// actions:
// const requestSubredditJson = (subreddit) => {
//     type: types.REQUEST_SUBREDDIT_JSON,
//     subreddit: subreddit
// };
// const receiveSubredditJson = (json) => {
//     type: types.RECEIVE_SUBREDDIT_JSON,
//     subredditData: json
// }

const fetchUser = () => {
    return dispatch => {
        dispatch(request_user)

        dispatch(set_loading_message("user profile"))
        axios_os.get(OS_API.APP_USER)
        .then(function (response) {
          // handle success
          dispatch(receive_user(response.data.user))
          dispatch(setLoadingProgress(100))
          dispatch(setLoaded(true))
          dispatch(setLoading(false))
        })
        .catch(function (error) {
          // handle error
          dispatch(setError(true))
          dispatch(setErrorMessage("Error loading user data"))
          dispatch(setErrorData(error.config.url))
        })
        .then(function () {
          // always executed
        });
    }
}

// operations:
// // 'fetchSubredditJson()' will fetch the JSON data from the subreddit,
// // extract the required information and update the Redux store with it.
// const fetchSubredditJson = (subreddit) => {
//     return dispatch => {
      
//       // Dispatching this action will toggle the 'showRedditSpinner'
//       // flag in the store, so that the UI can show a loading icon.
//       dispatch(requestSubredditJsonAction(subreddit));
//       return fetch(`https://www.reddit.com/r/${subreddit}.json`)
//         .then(response => response.json())
//         .then(json => {
//           const responseData = json;
//           let data = [];
        
//           responseData.data.children.map(child => {
//             const childData = {
//               title: child.data.title,
//               url: child.data.permalink
//             };
            
//             data.push(childData);
//             return null;
//           });
  
//         // Dispatching this action while passing the 'data' array 
//         // we created above will update the store with this data.
//         // It is good practice to send only the required information
//         // rather than trimming the data when and where it is used.
//         // This is why we aren't sending the entire JSON response to 
//         // the Redux store.
//         dispatch(receiveSubredditJsonAction(data))
//         });
//     }
//   };
  
//   export default {
//     incrementCount,
//     decrementCount,
//     fetchSubredditPosts
//   }

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
