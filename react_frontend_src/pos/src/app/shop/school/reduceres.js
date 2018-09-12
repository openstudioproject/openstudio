import { combineReducers } from 'redux';

import shopSchoolClasscardsReducer from './classcards/duck'
import shopSchoolSubscriptionsReducer from './subscriptions/duck'

const schoolReducer = combineReducers({
  classcards: shopSchoolClasscardsReducer,
  subscriptions: shopSchoolSubscriptionsReducer
});

export default schoolReducer
