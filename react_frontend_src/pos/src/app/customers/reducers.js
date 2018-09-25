import { combineReducers } from 'redux';
import listReducer from './list/duck'
import customersMembershipsReducer from './memberships/duck'

const customersReducer = combineReducers({
  list: listReducer,
  memberships: customersMembershipsReducer
})

export default customersReducer