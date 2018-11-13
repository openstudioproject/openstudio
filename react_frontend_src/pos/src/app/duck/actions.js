import T from './types'


export const requestPaymentMethods = () =>
    ({
        type: T.REQUEST_PAYMENT_METHODS
    })

export const receivePaymentMethods = (data) =>
    ({
        type: T.RECEIVE_PAYMENT_METHODS,
        data
    })

export const requestUser = () =>
    ({
        type: T.REQUEST_USER
    })

export const receiveUser = (data) =>
    ({
        type: T.RECEIVE_USER,
        data
    })

export const requestSettings = () =>
    ({
        type: T.REQUEST_SETTINGS
    })

export const receiveSettings = (data) =>
    ({
        type: T.RECEIVE_SETTINGS,
        data
    })

export const setError = (error) =>
    ({
        type: T.SET_ERROR,
        error
    })

export const setErrorData = (data) =>
    ({
        type: T.SET_ERROR_DATA,
        data
    })

export const setErrorMessage = (message) =>
    ({
        type: T.SET_ERROR_MESSAGE,
        message
    })

export const setLoaded = (loaded) =>
    ({
        type: T.SET_LOADED,
        loaded
    })

export const setLoading = (loading) =>
    ({
        type: T.SET_LOADING,
        loading
    })

export const setLoadingMessage = (message) =>
    ({
        type: T.SET_LOADING_MESSAGE,
        message
    })

export const setLoadingProgress = (progress) =>
    ({
        type: T.SET_LOADING_PROGRESS,
        progress
    })

export const setLocale = (locale) => 
    ({
        type: T.SET_LOCALE,
        locale
    })

export const setPageTitle = (title) =>
    ({
        type: T.SET_PAGE_TITLE,
        title
    })


export const requestSubmitCart = () =>
    ({
        type: T.REQUEST_SUBMIT_CART
    })


export const receiveSubmitCart = () =>
    ({
        type: T.RECEIVE_SUBMIT_CART
    })
    