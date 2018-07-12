import React, { Component } from 'react';

import {
  HashRouter as Router,
  Route, 
  Switch
} from 'react-router-dom';


import Home from './home/HomeContainer'
import PermissionsError from './permissions_error/PermissionsErrorContainer'
import Whoops404 from './whoops404/Whoops404'

import '../../stylesheets/app/App.scss'

class App extends Component {
  constructor(props) {
    super(props)
    console.log(this.props)
  }

  componentDidMount() {
    this.props.fetchUser()    
}

  render() {
    return (
      <Router>
          <Switch>
            <Route exact path='/' component={Home} />
            <Route path='/check-in' component={Home} />
            <Route path='/products' component={Home} />
            <Route path='/permissions_error' component={PermissionsError} />
            {/* Add all your remaining routes here, like /trending, /about, etc. */}
            <Route component={Whoops404} />
          </Switch>
      </Router>
    );
  }
}

export default App