import React, { Component } from 'react';

import {
  HashRouter as Router,
  Route, 
  Switch
} from 'react-router-dom';


import Customers from './customers/CustomersContainer'
import Classes from './checkin/classes/ClassesContainer'
import Attendance from './checkin/attendance/AttendanceContainer'
import Book from './checkin/book/BookContainer'
import Revenue from './checkin/revenue/RevenueContainer'
import Home from './home/HomeContainer'
import Classcards from './shop/school/classcards/ClasscardsContainer'
import Memberships from './shop/school/memberships/MembershipsContainer'
import Subscriptions from './shop/school/subscriptions/SubscriptionsContainer'
import PermissionsError from './permissions_error/PermissionsErrorContainer'
import Whoops404 from './whoops404/Whoops404'
import LoadingScreen from '../components/ui/LoadingScreen'

import '../../stylesheets/app/App.scss'

class App extends Component {
  constructor(props) {
    super(props)
    console.log(this.props)
  }

  componentWillMount() {
    this.props.fetchUser()    
    this.props.fetchSettings()  
    this.props.fetchCustomers()
    this.props.fetchShopSchoolClasscards()
    this.props.fetchShopSchoolMemberships()
    this.props.fetchShopSchoolSubscriptions()
  }


  render() {
    return (
      (this.props.app_state.loading) ? 
        <LoadingScreen progress={this.props.app_state.loading_progress}
        message={this.props.app_state.loading_message}/> :
      <Router>
          <Switch>
            <Route exact path='/' component={Home} />
            <Route exact path='/checkin' component={Classes} />
            <Route path='/checkin/attendance/:clsID' component={Attendance} />
            <Route path='/checkin/book/:clsID/:cuID' component={Book} />
            <Route path='/checkin/revenue/:clsID' component={Revenue} />
            <Route path='/customers' component= {Customers} />
            <Route path='/products/school/classcards' component={Classcards} />
            <Route path='/products/school/memberships' component={Memberships} />
            <Route path='/products/school/subscriptions' component={Subscriptions} />
            <Route path='/permissions_error' component={PermissionsError} />
            {/* Add all your remaining routes here, like /trending, /about, etc. */}
            <Route component={Whoops404} />
          </Switch>
      </Router>
    )
  }
}

export default App