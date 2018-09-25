import { combineReducers } from 'redux';
import { 
  appReducer,
  localeReducer,
 } from '../app/duck/reducers'
 import  checkinAttendanceReducer from '../app/checkin/attendance/duck'
 import  checkinBookReducer from '../app/checkin/book/duck'
 import  checkinClassesReducer from '../app/checkin/classes/duck'
 import  checkinRevenueReducer from '../app/checkin/revenue/duck'
 import customersReducer from '../app/customers/reducers'
 import shopReducer from '../app/shop/reducers'

const rootReducer = combineReducers({
  app: appReducer,
  locale: localeReducer,
  checkin_attendance: checkinAttendanceReducer,
  checkin_book: checkinBookReducer,
  checkin_classes: checkinClassesReducer,
  checkin_revenue: checkinRevenueReducer,
  customers: customersReducer,
  shop: shopReducer
  // home: homeReducer
});

export default rootReducer
