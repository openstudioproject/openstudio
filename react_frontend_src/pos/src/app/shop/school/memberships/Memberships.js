import React, { Component } from "react"
import { intlShape } from "react-intl"
import { v4 } from "uuid"
import PropTypes from "prop-types"

import ShopTemplate from '../../ShopTemplate'
import SchoolMenu from '../components/SchoolMenu'

import MembershipsList from './MembershipsList'

class Memberships extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        subscriptions: PropTypes.object,
        loaded: PropTypes.boolean,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.products' })
        )
        if (!this.props.loaded) {
            this.props.fetchShopMemberships()
        }
    }

    onClickMembership(membership) {
        console.log('clicked on:')
        console.log(membership)

        let item = {
           id: v4(),
           item_type: 'membership',
           quantity: 1,
           data: membership
        }

        console.log('item')
        console.log(item)
        // Check if item not yet in cart
        
        // If not yet in cart, add as a new pproduct, else increase 
        this.props.addToCart(item)
        
        // this.props.setDisplayCustomerID(id)
    }
    
    render() {
        return (
            <ShopTemplate app_state={this.props.app}>
                { this.props.loaded ? 
                     <SchoolMenu>
                         <br /><br />
                         <MembershipsList memberships={this.props.memberships} 
                                          currency_symbol={this.props.settings.currency_symbol} 
                                          onClick={this.onClickMembership.bind(this)} />
                     </SchoolMenu> :
                     "Loading..."
                }
            </ShopTemplate>
        )
    }
}

export default Memberships
