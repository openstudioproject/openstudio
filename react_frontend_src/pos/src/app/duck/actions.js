import T from './types'

export const setLoaderMessage = (message) =>
    ({
        type: T.SET_LOADER_MESSAGE,
        message
    })

export const setLoaderStatus = (status) =>
    ({
        type: T.SET_LOADER_STATUS,
        status
    })
