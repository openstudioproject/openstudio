// This file contains a default config for axios
import axios from 'axios'

const hostname = window && window.location && window.location.hostname
let backendHost

(hostname === 'dev.openstudioproject.com') ?
    backendHost = "http://dev.openstudioproject.com:8000" :
    backendHost = ""

const axios_os = axios.create({
    baseURL: backendHost,
    withCredentials: true,
    // headers: {
    //     'Accept': 'application/json',
    //     'Content-Type': 'application/json'
    // }
})

// Intercept failed requests due to not logged in for all requests
const notLoggedInInterceptor = axios_os.interceptors.response.use(
    function (response) {
        console.log(response)
        // catch user not logged in
        if (response.data.error == 401) {
            console.log('Redirecting to login...')
            window.location.href = response.data.location
        } else if (response.data.error == 403) {
            // Catch user permission denied
            console.log('Permissions error')
            console.log(response.data)
            window.location.href = response.data.location
            // setTimeout(() => window.location.reload(), 3000)
            return Promise.reject(response)
        }

        return response;
    },
    function (error) {
        return Promise.reject(error)
    }
)

export default axios_os