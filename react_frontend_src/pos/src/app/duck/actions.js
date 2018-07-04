import T from './types'

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

export const setLocale = (locale) => 
    ({
        type: T.SET_LOCALE,
        locale
    })


