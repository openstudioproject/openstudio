import T from './types'

export const shopSchoolClasscardsReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.SHOP_SCHOOL_SET_CLASSCARDS_LOADING:
            return {
                ...state,
                loading: action.loading,
            }
        case T.SHOP_SCHOOL_REQUEST_CLASSCARDS:
            return {
                loading: true,
                loaded: false,
                data: {}
            }
        case T.SHOP_SCHOOL_RECEIVE_CLASSCARDS:
            return {
                loading: false,
                loaded: true,
                data: action.data,
            }
        default:
            return {
                ...state
            }
    }
}
