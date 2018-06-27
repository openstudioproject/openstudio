import React from "react"
import ReactDOM from "react-dom"
import { Provider } from "react-redux"
import storeFactory from "./store"

import { setLoaderMessage, setLoaderStatus } from "./actions";

import {
  HashRouter,
  Route,
  Switch
} from 'react-router-dom'

import {
  POS,
  Whoops404 
} from './components/Pages'

const store = storeFactory()

store.dispatch(setLoaderStatus('loading'))
store.dispatch(setLoaderMessage('test'))
store.dispatch(setLoaderMessage('new state'))
store.dispatch(setLoaderStatus('done'))

ReactDOM.render(
  <Provider store={store}>
    <HashRouter>
        <Switch>
          <Route exact path="/" component={POS} />
          <Route component={Whoops404} />
        </Switch>
    </HashRouter>
  </Provider>,
  document.getElementById("app")
)