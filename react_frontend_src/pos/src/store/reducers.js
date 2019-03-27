import { combineReducers } from 'redux';
import { 
  appReducer,
  localeReducer,
 } from '../app/duck/reducers'

import checkinReducer from '../app/checkin/reducers'
import customersReducer from '../app/customers/reducers'
import cashbookReducer from '../app/cashbook/duck'
import shopReducer from '../app/shop/reducers'

const rootReducer = combineReducers({
  app: appReducer,
  locale: localeReducer,
  checkin: checkinReducer,
  customers: customersReducer,
  cashbook: cashbookReducer,
  shop: shopReducer
  // home: homeReducer
});

export default rootReducer
