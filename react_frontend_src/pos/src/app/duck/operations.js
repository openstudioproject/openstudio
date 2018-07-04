import {
    setLoading as set_loading,
    setLoadingMessage as set_loading_message
} from './actions'

const setLoadingMessage = set_loading_message
const setLoading = set_loading

// here data will be fetched

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
    setLoading,
    setLoadingMessage
}
