import React from "react";
import ReactDOM from "react-dom";

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
      <Switch>
        <Route exact path="/" component={POS} />
        <Route component={Whoops404} />
      </Switch>
  </HashRouter>, 
  document.getElementById("app")
)