import T from './types'


export const addItem = (data) =>
    ({
        type: T.ADD_ITEM,
        data
    })


export const deleteSelectedItem = () =>
    ({
        type: T.DELETE_SELECTED_ITEM
    })


export const setSelectedItem = (data) =>
    ({
        type: T.SET_SELECTED_ITEM,
        data
    })
