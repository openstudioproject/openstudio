import { combineReducers } from 'redux';
import { 
  appReducer,
  localeReducer,
 } from '../app/duck/reducers'

import classesReducer from '../app/classes/reducers'
import customersReducer from '../app/customers/reducers'
import cashbookReducer from '../app/cashbook/duck'
import shopReducer from '../app/shop/reducers'

const rootReducer = combineReducers({
  app: appReducer,
  locale: localeReducer,
  classes: classesReducer,
  customers: customersReducer,
  cashbook: cashbookReducer,
  shop: shopReducer
  // home: homeReducer
});

export default rootReducer
