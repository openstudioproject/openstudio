import { combineReducers } from 'redux';

import schoolReducer from './school/reduceres'

const shopReducer = combineReducers({
  school: schoolReducer,
});

export default shopReducer
