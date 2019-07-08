import T from './types'

export const requestSchoolInfo = () =>
    ({
        type: T.REQUEST_CUSTOMER_SCHOOL_INFO
    })

export const receiveSchoolInfo = (data) =>
    ({
        type: T.RECEIVE_CUSTOMER_SCHOOL_INFO,
        data
    })