import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import ShopTemplate from '../../components/ShopTemplate'
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
    }
    
    render() {
        return (
            <ShopTemplate app_state={this.props.app}>
                { this.props.loaded ? 
                     <SchoolMenu>
                         <br /><br />
                         <MembershipsList memberships={this.props.memberships} 
                                          currency_symbol={this.props.settings.currency_symbol} 
                                            />
                     </SchoolMenu> :
                     "Loading..."
                }
            </ShopTemplate>
        )
    }
}

export default Memberships
