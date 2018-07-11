import React, { Component } from 'react';

import {
  HashRouter as Router,
  Route, 
  Switch
} from 'react-router-dom';


import Home from './home/HomeContainer'
import Whoops404 from './whoops404/Whoops404'

import '../../stylesheets/app/App.scss'

class App extends Component {
  constructor(props) {
    super(props)
  }

  componentDidMount() {
    this.props.fetchUser()

    // setTimeout(() => this.props.setLoadingMessage('phase 1'), 500)
    // setTimeout(() => this.props.setLoadingProgress(100), 500)
    // // setTimeout(() => this.props.setLoadingMessage('phase 2'), 1500)
    // // setTimeout(() => this.props.setLoadingProgress(66), 1500)
    // // setTimeout(() => this.props.setLoadingMessage('phase 3'), 2500)
    // // setTimeout(() => this.props.setLoadingProgress(100), 2500)

    // ready...
    // const loaded_timeout = 1000
    // setTimeout(() => this.props.setLoading(false), loaded_timeout)
    // setTimeout(() => this.props.setLoaded(true), loaded_timeout) 
    // setTimeout(() => this.props.setLoadingMessage('Loading done!'), loaded_timeout)
    // this.props.setLoading(false)
    // this.props.setLoaded(true)
    // this.props.setLoadingMessage('Loading done!')
    
}

  render() {
    return (
      <Router>
          <Switch>
            <Route exact path='/' component={Home} />
            <Route path='/check-in' component={Home} />
            <Route path='/products' component={Home} />
            {/* Add all your remaining routes here, like /trending, /about, etc. */}
            <Route component={Whoops404} />
          </Switch>
      </Router>
    );
  }
}

export default App