import { combineReducers } from 'redux';
import  homeReducer  from '../app/home/duck/reducers'

const rootReducer = combineReducers({
  home: homeReducer
});

export default rootReducer;
