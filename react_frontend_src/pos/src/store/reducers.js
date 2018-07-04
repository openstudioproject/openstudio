import { combineReducers } from 'redux';
import { 
  appReducer,
  localeReducer 
 } from '../app/duck/reducers'
import  homeReducer  from '../app/home/duck/reducers'

const rootReducer = combineReducers({
  app: appReducer,
  locale: localeReducer,
  home: homeReducer
});

export default rootReducer;
