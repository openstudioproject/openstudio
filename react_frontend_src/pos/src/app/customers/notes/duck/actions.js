import T from './types'

export const requestNotes = () =>
    ({
        type: T.REQUEST_NOTES
    })

export const receiveNotes = () =>
    ({
        type: T.RECEIVE_NOTES
    })

export const requestCreateNote = () =>
    ({
        type: T.REQUEST_CREATE_NOTE
    })

export const receiveCreateNotes = () =>
    ({
        type: T.RECEIVE_CREATE_NOTE
    })

export const requestUpdateNote = () =>
    ({
        type: T.REQUEST_UPDATE_NOTE
    })

export const receiveUpdateNote = () =>
    ({
        type: T.RECEIVE_UPDATE_NOTE
    })

export const requestUpdateNoteStatus = () =>
    ({
        type: T.REQUEST_UPDATE_NOTE_STATUS
    })

export const receiveUpdateNoteStatus = () =>
    ({
        type: T.RECEIVE_UPDATE_NOTE_STATUS
    })

export const requestDeleteNote = () =>
    ({
        type: T.REQUEST_DELETE_NOTE
    })

export const receiveDeleteNote = () =>
    ({
        type: T.RECEIVE_DELETE_NOTE
    })
