import React, { Component } from 'react';

import {
  BrowserRouter as Router,
  Route, 
  Switch
} from 'react-router-dom';

import Home from './home/HomeContainer'
import Whoops404 from './whoops404/Whoops404'

class App extends Component {
  // perhaps a componentDidMount here to dispatch fetch data operations??

  render() {
    return (
      <Router>
        <div>
          <Switch>
            <Route exact path='/' component={Home} />
            <Route exact path='/pos' component={Home} />
            <Route path='/pos/check-in' component={Home} />
            <Route path='/pos/products' component={Home} />
            {/* Add all your remaining routes here, like /trending, /about, etc. */}
            <Route component={Whoops404} />
          </Switch>
        </div>
      </Router>
    );
  }
}

export default App