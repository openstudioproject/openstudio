// This file contains a default config for axios
import axios from 'axios'

const hostname = window && window.location && window.location.hostname
let backendHost

(hostname === 'localhost') ?
    backendHost = "http://dev.openstudioproject.com:8000" :
    backendHost = ""

const axios_os = axios.create({
    baseURL: backendHost,
    withCredentials: true
})

// Intercept failed requests due to not logged in for all requests
const notLoggedInInterceptor = axios_os.interceptors.response.use(function (response) {
    // catch user not logged in
    if (response.data.error == 403) {
        console.log('redirecting to login...')
        setTimeout(() => window.location.replace(response.data.location), 10000)
    }
    
    return response;
})

export default axios_os