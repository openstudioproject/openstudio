import { combineReducers } from 'redux';
import { 
  appReducer,
  localeReducer,
  userReducer 
 } from '../app/duck/reducers'
 import  checkinClassesReducer from '../app/checkin/classes/duck'
 import  checkinAttendanceReducer from '../app/checkin/attendance/duck'

 console.log(checkinAttendanceReducer)
//  import  homeReducer  from '../app/home/duck/reducers'


const rootReducer = combineReducers({
  app: appReducer,
  locale: localeReducer,
  user: userReducer,
  checkin_classes: checkinClassesReducer,
  checkin_attendance: checkinAttendanceReducer
  // home: homeReducer
});

export default rootReducer
