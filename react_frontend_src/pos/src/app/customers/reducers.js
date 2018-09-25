import { combineReducers } from 'redux';
import listReducer from './list/duck'

const customersReducer = combineReducers({
  list: listReducer
})

export default customersReducer