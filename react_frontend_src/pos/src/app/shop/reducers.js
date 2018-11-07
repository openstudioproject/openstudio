import { combineReducers } from 'redux';

import productsRecucer from './products/duck'
import schoolReducer from './school/reduceres'
import shopCartReducer from './cart/duck';
import shopPaymentReducer from './payment/duck';

const shopReducer = combineReducers({
  payment: shopPaymentReducer,
  products: productsRecucer,
  school: schoolReducer,
  cart: shopCartReducer,
});

export default shopReducer
