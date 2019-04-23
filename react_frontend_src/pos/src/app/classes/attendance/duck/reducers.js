import T from './types'

export const classesAttendanceReducer = (state = {}, action={ type: null }) => {
    switch (action.type) {
        case T.CLASSES_SET_CLASS_ATTENDANCE_LOADING:
            return {
                ...state,
                loading: action.loading,
            }
        case T.CLASSES_REQUEST_CLASS_ATTENDANCE:
            return {
                ...state,
                loading: true,
                loaded: false,
                data: {}
            }
        case T.CLASSES_RECEIVE_CLASS_ATTENDANCE:
            return {
                ...state,
                loading: false,
                loaded: true,
                data: action.data.attendance,
            }
        case T.CLASSES_CLASS_ATTENDANCE_REQUEST_UPDATE_STATUS:
            // Append classes attendance ID, so we can show it as updating
            return {
                ...state,
                attendanceStatusUpdating: [
                    ...state.attendanceStatusUpdating,
                    action.clattID
                    ]
            }
        case T.CLASSES_CLASS_ATTENDANCE_RECEIVE_UPDATE_STATUS:
            // Filter classes attendance ID, so we know it's no longer updating
            // And update booking status
            // Find array item
            console.log(action)
            let clattID = action.data.clattID

            function findClattID(item) {
                return item.classes_attendance.id == clattID
            }
            // state.data[index].classes_attendance = action.data.status
            // console.log(state.data.findIndex(findClattID))


            return {
                ...state,
                data: state.data.map(
                    (item, i) => i === state.data.findIndex(findClattID) ? {
                        ...item, 
                        classes_attendance: {
                            ...item.classes_attendance, 
                            BookingStatus: action.data.status
                        }
                    } : item
                ),
                attendanceStatusUpdating: state.attendanceStatusUpdating.filter(
                    (item, index) => item != clattID
                )
            }
        case T.CLASSES_CLASS_ATTENDANCE_REQUEST_DELETE:
            // Append classes attendance ID, so we can show it as deleting
            return {
                ...state,
                attendanceStatusDeleting: [
                    ...state.attendanceDeleting,
                    action.clattID
                    ]
            }
        case T.CLASSES_CLASS_ATTENDANCE_RECEIVE_DELETE:
            // Filter classes attendance ID, so we know it's no longer deleting
            // And update booking status
            // Find array item
            console.log(action)
            let clattID_delete = action.data.clattID

            function findClattID(item) {
                return item.classes_attendance.id == clattID_delete
            }
            // state.data[index].classes_attendance = action.data.status
            // console.log(state.data.findIndex(findClattID))

            return {
                ...state,
                data: state.data.filter(
                    (item, index) => index !== state.data.findIndex(findClattID)
                ),
                attendanceDeleting: state.attendanceDeleting.filter(
                    (item, index) => item != clattID_delete
                )
            }
        case T.CLASSES_SET_CLASS_ATTENDANCE_SEARCH_CUSTOMER_ID:
            return {
                ...state,
                search_customer_id: action.search_customer_id,
            }
        case T.CLASSES_ATTENDANCE_CLEAR_SEARCH_TIMEOUT:
            return {
                ...state,
                searchTimeout: clearTimeout(state.searchTimeout),
                
            }
        case T.CLASSES_ATTENDANCE_SET_SEARCH_TIMEOUT:
            return {
                ...state,
                searchTimeout: action.timeout,
            }
        case T.CLASSES_ATTENDANCE_CLEAR_SEARCH_CUSTOMER_ID:
            return {
                ...state,
                searchCustomerID: null,
            }
        case T.CLASSES_ATTENDANCE_SET_SEARCH_CUSTOMER_ID:
            return {
                ...state,
                searchCustomerID: action.id,
            }
        case T.CLASSES_ATTENDANCE_CLEAR_SEARCH_VALUE:
            return {
                ...state,
                searchValue: "",
            }
        case T.CLASSES_ATTENDANCE_SET_SEARCH_VALUE:
            return {
                ...state,
                searchValue: action.value.toLowerCase(),
            }
        default:
            return {
                ...state
            }
    }
}
