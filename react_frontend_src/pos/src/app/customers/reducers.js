import { combineReducers } from 'redux';
import listReducer from './list/duck'
import membershipsReducer from './memberships/duck'

const customersReducer = combineReducers({
  list: listReducer,
  memberships: membershipsReducer
})

export default customersReducer