import { combineReducers } from 'redux';

import classesAttendanceReducer from "./attendance/duck"
import classesBookReducer from "./book/duck"
import classesClassesReducer from "./classes/duck"
import classesRevenueReducer from "./revenue/duck"

const classesReducer = combineReducers({
  attendance: classesAttendanceReducer,
  book: classesBookReducer,
  classes: classesClassesReducer,
  revenue: classesRevenueReducer,
});

export default classesReducer
