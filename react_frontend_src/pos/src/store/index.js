import { createStore, combineReducers, applyMiddleware } from 'redux'
import logger from 'redux-logger'
import thunk from 'redux-thunk'
import rootReducer from './reducers'
import stateData from '../../data/initialState'

let console = window.console

// const logger = store => next => action => {
//     let result
//     console.groupCollapsed("dispatching", action.type)
//     console.log('prev state', store.getState())
//     console.log('action', action)
//     result = next(action)
//     console.log('next state', store.getState())
//     console.groupEnd()
//     return result
// }

const saver = store => next => action => {
    let result = next(action)
    localStorage['redux-store'] = JSON.stringify(store.getState())
    return result
}

// const storeFactory = (initialState=stateData) =>
//     applyMiddleware(logger, saver)(createStore)(
//         combineReducers({pos: loader}),
//         (localStorage['redux-store']) ?
//             JSON.parse(localStorage['redux-store']) :
//             initialState
//     )
// no local storage
// const storeFactory = (initialState=stateData) =>
//     applyMiddleware(thunk, logger)(createStore)(
//         combineReducers({root: rootReducer}), 
//         initialState
//     )
const storeFactory = (initialState=stateData) =>
    applyMiddleware(thunk, logger)(createStore)(
        rootReducer, 
        initialState
    )

export default storeFactory