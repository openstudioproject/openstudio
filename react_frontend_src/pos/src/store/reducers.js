import { combineReducers } from 'redux';
import  appReducer  from '../app/duck/reducers'
import  homeReducer  from '../app/home/duck/reducers'

const rootReducer = combineReducers({
  app: appReducer,
  home: homeReducer
});

export default rootReducer;
