import T from './types'


export const requestCheckinClasses = () =>
    ({
        type: T.CHECKIN_REQUEST_CLASSES
    })

export const receiveCheckinClasses = (data) =>
    ({
        type: T.CHECKIN_RECEIVE_CLASSES,
        data
    })

export const setCheckinClassesLoaded = (loaded) =>
    ({
        type: T.CHECKIN_SET_CLASSES_LOADED,
        loaded
    })

export const setCheckinClassesLoading = (loading) =>
    ({
        type: T.CHECKIN_SET_CLASSES_LOADING,
        loading
    })

    