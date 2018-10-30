import T from './types'


export const addItem = (data) =>
    ({
        type: T.ADD_ITEM,
        data
    })
