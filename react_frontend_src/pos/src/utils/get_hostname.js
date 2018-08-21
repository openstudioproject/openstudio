
const hostname = window && window.location && window.location.hostname
let backendHost

(hostname === 'localhost') ?
    backendHost = "http://dev.openstudioproject.com:8000" :
    backendHost = ""

export default backendHost
