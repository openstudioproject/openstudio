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
  Welcome,
  POS,
  Whoops404 
} from './components/Pages'

import { App } from "./components/App"

const store = storeFactory()
console.log(store.getState())

ReactDOM.render(
  <Provider store={store}>
    <HashRouter>
        <Switch>
          <Route exact path="/" component={App} />
          <Route component={Whoops404} />
        </Switch>
    </HashRouter>
  </Provider>,
  document.getElementById("app")
)