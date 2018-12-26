import T from './types'
import { bindActionCreators } from 'redux';


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

export const setPageSubTitle = (subtitle) =>
    ({
        type: T.SET_PAGE_SUBTITLE,
        subtitle
    })

export const clearPageSubTitle = () =>
    ({
        type: T.CLEAR_PAGE_SUBTITLE
    })


export const requestValidateCart = () =>
    ({
        type: T.REQUEST_VALIDATE_CART
    })


export const receiveValidateCart = (data) =>
    ({
        type: T.RECEIVE_VALIDATE_CART,
        data
    })
    