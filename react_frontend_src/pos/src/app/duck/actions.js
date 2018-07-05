import T from './types'

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

