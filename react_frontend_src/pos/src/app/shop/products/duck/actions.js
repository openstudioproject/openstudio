import T from './types'


export const requestProducts = () =>
    ({
        type: T.REQUEST_PRODUCTS
    })

export const receiveProducts = (data) =>
    ({
        type: T.RECEIVE_PRODUCTS,
        data
    })

export const requestProductCategories = () =>
    ({
        type: T.REQUEST_PRODUCT_CATEGORIES
    })

export const receiveProductCategories = (data) =>
    ({
        type: T.RECEIVE_PRODUCT_CATEGORIES,
        data
    })

export const clearSearchTimeout = () =>
    ({
        type: T.CLEAR_SEARCH_TIMEOUT
    })

export const setSearchTimeout = (timeout) =>
    ({
        type: T.SET_SEARCH_TIMEOUT,
        timeout,
    })

export const clearSearchProductID = () =>
    ({
        type: T.CLEAR_SEARCH_PRODUCT_ID
    })

export const setSearchProductID = (id) =>
    ({
        type: T.SET_SEARCH_PRODUCT_ID,
        id
    })

export const clearProductsSearchValue = () =>
    ({
        type: T.CLEAR_PRODUCTS_SEARCH_VALUE
    })

export const setProductsSearchValue = (value) =>
    ({
        type: T.SET_PRODUCTS_SEARCH_VALUE,
        value
    })

export const clearCategoryFilterID = () =>
    ({
        type: T.CLEAR_CATEGORY_FILTER_ID
    })

export const setCategoryFilterID = (id) =>
    ({
        type: T.SET_CATEGORY_FILTER_ID,
        id
    })