import {
    requestProducts,
    receiveProducts,
    requestProductCategories,
    receiveProductCategories,
    clearSearchTimeout,
    clearProductsSearchValue,
    clearSearchProductID,
    clearCategoryFilterID,
    setSearchTimeout,
    setProductsSearchValue,
    setSearchProductID,
    setCategoryFilterID
} from './actions'

import axios_os from '../../../../utils/axios_os'
import OS_API from '../../../../utils/os_api'

// just pass these actions as there's nothing else they need to do
// Put pass-through actions here

// data fetchers
const fetchProducts = () => {
      return dispatch => {
          dispatch(requestProducts())

          axios_os.get(OS_API.SHOP_PRODUCTS)
          .then(function (response) {
            // handle success
            dispatch(receiveProducts(response.data))
            // dispatch(setLoadingProgress(100))
          })
          .catch(function (error) {
            // handle error
            console.log(error)
          })
          .then(function () {
            // always executed
          });
      }
  }

  const fetchProductCategories = () => {
    return dispatch => {
        dispatch(requestProductCategories)
  
        axios_os.get(OS_API.SHOP_PRODUCT_CATEGORIES)
        .then(function (response) {
          // handle success
          console.log('Receive products categories here')
          dispatch(receiveProductCategories(response.data))    
        })
        .catch(function (error) {
          // handle error
          console.log(error)
        })
        .then(function () {
          // always executed
        });
    }
  }
  


export default {
    fetchProducts,
    fetchProductCategories,
    clearSearchTimeout,
    clearProductsSearchValue,
    clearSearchProductID,
    clearCategoryFilterID,
    setSearchTimeout,
    setProductsSearchValue,
    setSearchProductID,
    setCategoryFilterID
}
