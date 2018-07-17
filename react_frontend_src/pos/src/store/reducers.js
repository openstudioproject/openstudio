import { combineReducers } from 'redux';
import { 
  appReducer,
  localeReducer,
  userReducer 
 } from '../app/duck/reducers'
 import  checkinClassesReducer from '../app/checkin/classes/duck'
//  import  homeReducer  from '../app/home/duck/reducers'


const rootReducer = combineReducers({
  app: appReducer,
  locale: localeReducer,
  user: userReducer,
  checkin_classes: checkinClassesReducer,
  // home: homeReducer
});

export default rootReducer
