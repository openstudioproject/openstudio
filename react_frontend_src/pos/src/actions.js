import C from './constants'

export const setLoaderMessage = (message) =>
    ({
        type: C.SET_LOADER_MESSAGE,
        message
    })

export const setLoaderStatus = (status) =>
    ({
        type: C.SET_LOADER_STATUS,
        status
    })
