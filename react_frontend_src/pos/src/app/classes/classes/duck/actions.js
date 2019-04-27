import T from './types'


export const requestClassesClasses = () =>
    ({
        type: T.CLASSES_REQUEST_CLASSES
    })

export const receiveClassesClasses = (data) =>
    ({
        type: T.CLASSES_RECEIVE_CLASSES,
        data
    })

export const setClassesClassesLoaded = (loaded) =>
    ({
        type: T.CLASSES_SET_CLASSES_LOADED,
        loaded
    })

export const setClassesClassesLoading = (loading) =>
    ({
        type: T.CLASSES_SET_CLASSES_LOADING,
        loading
    })

    