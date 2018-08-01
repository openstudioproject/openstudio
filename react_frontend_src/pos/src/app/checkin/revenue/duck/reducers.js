import T from './types'

export const checkinRevenueReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.CHECKIN_SET_REVENUE_LOADING:
            return {
                ...state,
                revenue_loading: action.loading,
            }
        case T.CHECKIN_REQUEST_REVENUE:
            return {
                ...state,
                revenue_loading: true,
                revenue_loaded: false,
                revenue: {}
            }
        case T.CHECKIN_RECEIVE_REVENUE:
            return {
                ...state,
                revenue_loading: false,
                revenue_loaded: true,
                revenue: action.data.revenue,
            }
        case T.CHECKIN_REQUEST_TEACHER_PAYMENT:
            return {
                ...state,
                teacher_payment_loading: true,
                teacher_payment_loaded: false,
                teacher_payment: {}                
            }
        case T.CHECKIN_RECEIVE_TEACHER_PAYMENT:
            console.log('reducer here')
            console.log(action.data)

            return {
                ...state,
                teacher_payment_loading: false,
                teacher_payment_loaded: true,
                teacher_payment: action.data.payment   
            }
        case T.CHECKIN_REQUEST_VERIFY_TEACHER_PAYMENT:
            return {
                ...state
            }
        default:
            return {
                ...state
            }
    }
}
