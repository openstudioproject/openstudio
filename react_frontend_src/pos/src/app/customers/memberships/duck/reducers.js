import T from './types'

export const customersMembershipsReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.REQUEST_CUSTOMERS_MEMBERSHIPS:
            return {
                loading: true,
                loaded: false,
                loading: action.loading,
            }
        case T.RECEIVE_CUSTOMERS_MEMBERSHIPS:
            return {
                loading: false,
                loaded: true,
                data: action.data
            }
    }
}


