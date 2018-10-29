import { combineReducers } from 'redux';

import productsRecucer from './products/duck'
import schoolReducer from './school/reduceres'

const shopReducer = combineReducers({
  products: productsRecucer,
  school: schoolReducer,
});

export default shopReducer
