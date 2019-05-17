import T from './types'


export const requestCustomers = () =>
    ({
        type: T.REQUEST_CUSTOMERS
    })

export const receiveCustomers = (data) =>
    ({
        type: T.RECEIVE_CUSTOMERS,
        data
    })

export const requestCreateCustomer = (data) =>
    ({
        type: T.REQUEST_CREATE_CUSTOMER,
        data
    })

export const receiveCreateCustomer = (data) =>
    ({
        type: T.RECEIVE_CREATE_CUSTOMER,
        data
    })

export const clearCreateCustomerErrorData = () =>
    ({
        type: T.CLEAR_CREATE_CUSTOMER_ERROR_DATA
    })

export const requestUpdateCustomer = (data) =>
    ({
        type: T.REQUEST_UPDATE_CUSTOMER,
        data
    })

export const receiveUpdateCustomer = (data) =>
    ({
        type: T.RECEIVE_UPDATE_CUSTOMER,
        data
    })

export const clearUpdateCustomerErrorData = () =>
    ({
        type: T.CLEAR_UPDATE_CUSTOMER_ERROR_DATA
    })

export const requestSaveCameraAppSnap = () =>
    ({
        type: T.REQUEST_SAVE_CAMERA_APP_SNAP
    })

export const receiveSaveCameraAppSnap = (data) =>
    ({
        type: T.RECEIVE_SAVE_CAMERA_APP_SNAP,
        data
    })

export const clearSearchTimeout = () =>
    ({
        type: T.CLEAR_SEARCH_TIMEOUT
    })

export const setSearchTimeout = (timeout) =>
    ({
        type: T.SET_SEARCH_TIMEOUT,
        timeout,
    })

export const clearDisplayCustomerID = () =>
    ({
        type: T.CLEAR_DISPLAY_CUSTOMER_ID
    })

export const setDisplayCustomerID = (id) =>
    ({
        type: T.SET_DISPLAY_CUSTOMER_ID,
        id
    })

export const clearSearchCustomerID = () =>
    ({
        type: T.CLEAR_SEARCH_CUSTOMER_ID
    })

export const setSearchCustomerID = (id) =>
    ({
        type: T.SET_SEARCH_CUSTOMER_ID,
        id
    })

export const clearSearchValue = () =>
    ({
        type: T.CLEAR_SEARCH_VALUE
    })

export const setSearchValue = (value) =>
    ({
        type: T.SET_SEARCH_VALUE,
        value
    })

export const clearSelectedCustomerID = () =>
    ({
        type: T.CLEAR_SELECTED_CUSTOMER_ID
    })

export const setSelectedCustomerID = (id) =>
    ({
        type: T.SET_SELECTED_CUSTOMER_ID,
        id
    })

export const setCreateCustomerStatus = (status) =>
    ({
        type: T.SET_CREATE_CUSTOMER_STATUS,
        status
    })

export const setUpdateCustomerStatus = (status) =>
    ({
        type: T.SET_UPDATE_CUSTOMER_STATUS,
        status
    })

export const setRedirectNextComponent = (component) =>
    ({
        type: T.SET_REDIRECT_NEXT_COMPONENT,
        component
    })

export const clearRedirectNextComponent = () =>
    ({
        type: T.CLEAR_REDIRECT_NEXT_COMPONENT,
    })

export const setCameraAppSnap = (data) =>
    ({
        type: T.SET_CAMERA_APP_SNAP,
        data
    })

export const clearCameraAppSnap = () =>
    ({
        type: T.CLEAR_CAMERA_APP_SNAP,
    })

export const requestNotes = () =>
    ({
        type: T.REQUEST_NOTES
    })

export const receiveNotes = (data) =>
    ({
        type: T.RECEIVE_NOTES,
        data
    })

export const clearNotes = () =>
    ({
        type: T.CLEAR_NOTES
    })

export const setCreateNote = () =>
    ({
        type: T.SET_CREATE_NOTE
    })

export const clearCreateNote = () =>
    ({
        type: T.CLEAR_CREATE_NOTE
    })

export const requestCreateNote = () =>
    ({
        type: T.REQUEST_CREATE_NOTE
    })

export const receiveCreateNote = (data) =>
    ({
        type: T.RECEIVE_CREATE_NOTE,
        data
    })

export const setUpdateNote = (id) =>
    ({
        type: T.SET_UPDATE_NOTE,
        id
    })

export const clearUpdateNote = () =>
    ({
        type: T.CLEAR_UPDATE_NOTE
    })

export const deleteNote = (id) =>
    ({
        type: T.DELETE_NOTE,
        id
    })