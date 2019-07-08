import { combineReducers } from 'redux';
import listReducer from './list/duck'
import customersClasscardsReducer from './classcards/duck'
import customersSubscriptionsReducer from './subscriptions/duck'
import customersMembershipsReducer from './memberships/duck'
import customersMembershipsTodayReducer from './memberships_today/duck'
import customersSchoolInfoReducer from './school_info/duck'

const customersReducer = combineReducers({
  list: listReducer,
  classcards: customersClasscardsReducer,
  subscriptions: customersSubscriptionsReducer,
  memberships: customersMembershipsReducer,
  memberships_today: customersMembershipsTodayReducer,
  school_info: customersSchoolInfoReducer
})

export default customersReducer