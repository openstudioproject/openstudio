import { combineReducers } from 'redux';
import { 
  appReducer,
  localeReducer,
 } from '../app/duck/reducers'

import checkinReducer from '../app/checkin/reducers'
import customersReducer from '../app/customers/reducers'
import shopReducer from '../app/shop/reducers'

const rootReducer = combineReducers({
  app: appReducer,
  locale: localeReducer,
  checkin: checkinReducer,
  customers: customersReducer,
  shop: shopReducer
  // home: homeReducer
});

export default rootReducer
