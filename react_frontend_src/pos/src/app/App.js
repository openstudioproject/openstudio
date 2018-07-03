import React, { Component } from 'react';

import {
  BrowserRouter as Router,
  Route, 
  Switch
} from 'react-router-dom';

import Home from './home/HomeContainer'
import Whoops404 from './whoops404/Whoops404'

class App extends Component {
  render() {
    return (
      <Router>
        <div>
          <Switch>
            <Route exact path='/' component={Home} />
            <Route path='/home'   component={Home} />
            {/* Add all your remaining routes here, like /trending, /about, etc. */}
            <Route component={Whoops404} />
          </Switch>
        </div>
      </Router>
    );
  }
}

export default App