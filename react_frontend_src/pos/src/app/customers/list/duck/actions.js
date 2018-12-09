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