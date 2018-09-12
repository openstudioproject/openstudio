import { combineReducers } from 'redux';

import shopSchoolClasscardsReducer from './classcards/duck'

const schoolReducer = combineReducers({
  classcards: shopSchoolClasscardsReducer,
});

export default schoolReducer
