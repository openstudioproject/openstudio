import { combineReducers } from 'redux';
import listReducer from './list/duck'
import customersMembershipsReducer from './memberships/duck'
import customersMembershipsTodayReducer from './memberships_today/duck'

const customersReducer = combineReducers({
  list: listReducer,
  memberships: customersMembershipsReducer,
  memberships_today: customersMembershipsTodayReducer
})

export default customersReducer