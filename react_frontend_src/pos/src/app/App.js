import React, { Component } from 'react';
import {
  BrowserRouter as Router,
  Route
} from 'react-router-dom';
import Home from './home/HomeContainer';

class App extends Component {
  render() {
    return (
      <Router>
        <div>
          <Route exact path='/' component={Home}/>
          <Route path='/home'   component={Home}/>
          {/* Add all your remaining routes here, like /trending, /about, etc. */}
        </div>
      </Router>
    );
  }
}

export default App