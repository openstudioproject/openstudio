import { combineReducers } from 'redux';

import productsRecucer from './products/duck'
import schoolReducer from './school/reduceres'
import shopCartReducer from './cart/duck';

const shopReducer = combineReducers({
  products: productsRecucer,
  school: schoolReducer,
  cart: shopCartReducer,
});

export default shopReducer
