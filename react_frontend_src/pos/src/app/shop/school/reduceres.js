import { combineReducers } from 'redux';

import shopSchoolClasscardsReducer from './classcards/duck'
import shopSchoolMembershipsReducer from './memberships/duck'
import shopSchoolSubscriptionsReducer from './subscriptions/duck'

const schoolReducer = combineReducers({
  classcards: shopSchoolClasscardsReducer,
  memberships: shopSchoolMembershipsReducer,
  subscriptions: shopSchoolSubscriptionsReducer
});

export default schoolReducer
