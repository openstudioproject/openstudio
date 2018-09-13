import T from './types'

export const shopSchoolMembershipsReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.SHOP_SCHOOL_SET_MEMBERSHIPS_LOADING:
            return {
                ...state,
                loading: action.loading,
            }
        case T.SHOP_SCHOOL_REQUEST_MEMBERSHIPS:
            return {
                loading: true,
                loaded: false,
                data: {}
            }
        case T.SHOP_SCHOOL_RECEIVE_MEMBERSHIPS:
            return {
                loading: false,
                loaded: true,
                data: action.data.data,
            }
        default:
            return {
                ...state
            }
    }
}
