import { combineReducers } from 'redux';

import checkinAttendanceReducer from "./attendance/duck"
import checkinBookReducer from "./book/duck"
import checkinClassesReducer from "./classes/duck"
import checkinRevenueReducer from "./revenue/duck"

const checkinReducer = combineReducers({
  attendance: checkinAttendanceReducer,
  book: checkinBookReducer,
  classes: checkinClassesReducer,
  revenue: checkinRevenueReducer,
});

export default checkinReducer
