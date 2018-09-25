import T from './types'

export const customersMembershipsReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.REQUEST_MEMBERSHIPS:
            return {
                loading: true,
                loaded: false,
                loading: action.loading,
            }
        case T.RECEIVE_MEMBERSHIPS:
            return {
                loading: false,
                loaded: true,
                data: action.data
            }
        default:
            return {
                ...state
            }
    }
}
