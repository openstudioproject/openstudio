import T from './types'

export const classesRevenueReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.CLASSES_SET_REVENUE_LOADING:
            return {
                ...state,
                revenue_loading: action.loading,
            }
        case T.CLASSES_REQUEST_REVENUE:
            return {
                ...state,
                revenue_loading: true,
                revenue_loaded: false,
                revenue: {}
            }
        case T.CLASSES_RECEIVE_REVENUE:
            return {
                ...state,
                revenue_loading: false,
                revenue_loaded: true,
                revenue: action.data.revenue,
            }
        case T.CLASSES_REQUEST_TEACHER_PAYMENT:
            return {
                ...state,
                teacher_payment_loading: true,
                teacher_payment_loaded: false,
                teacher_payment: {}                
            }
        case T.CLASSES_RECEIVE_TEACHER_PAYMENT:
            return {
                ...state,
                teacher_payment_loading: false,
                teacher_payment_loaded: true,
                teacher_payment: action.data.payment   
            }
        case T.CLASSES_REQUEST_VERIFY_TEACHER_PAYMENT:
            return {
                ...state,
                teacher_payment_verifying: true
            }
        case T.CLASSES_RECEIVE_VERIFY_TEACHER_PAYMENT:
            return {
                ...state,
                teacher_payment_verifying: false,
                teacher_payment: {
                    ...state.teacher_payment,
                    data: {
                        ...state.teacher_payment.data,
                        Status: 'verified'
                    }
                    
                }
            }
        default:
            return {
                ...state
            }
    }
}
