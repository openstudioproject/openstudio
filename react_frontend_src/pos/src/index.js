import React from "react";
import ReactDOM from "react-dom";

import App from "./components/App"

import {
  HashRouter,
  Route,
  Switch
} from 'react-router-dom'

import {
  POS,
  Whoops404 
} from './components/Pages'


ReactDOM.render(
  <HashRouter>
    <div className="main">
      <Switch>
        <Route exact path="/" component={POS} />
        <Route component={Whoops404} />
      </Switch>
    </div>
  </HashRouter>, 
  document.getElementById("app")
)