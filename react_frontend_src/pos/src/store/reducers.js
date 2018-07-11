import { combineReducers } from 'redux';
import { 
  appReducer,
  localeReducer,
  userReducer 
 } from '../app/duck/reducers'
import  homeReducer  from '../app/home/duck/reducers'

const rootReducer = combineReducers({
  app: appReducer,
  locale: localeReducer,
  user: userReducer,
  home: homeReducer
});

export default rootReducer;
