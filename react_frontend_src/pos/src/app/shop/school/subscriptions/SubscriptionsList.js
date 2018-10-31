import React, {Component} from "react"
import { v4 } from "uuid"

import SubscriptionsListItem from "./SubscriptionsListItem";


class SubscriptionsList extends Component {
    constructor(props) {
        super(props)
    }

    populateRows = (subscriptions) => {
        let container = []
        let children = []
        subscriptions.map((subscription, i) => {
            console.log(i)
            console.log(subscription)
            children.push(<SubscriptionsListItem key={"subscription_" + v4()}
                                                 data={subscription}
                                                 currency_symbol={this.props.currency_symbol}
                                                 onClick={() => this.props.onClick(subscription)} />)
            if (( (i+1) % 3 ) === 0 || i+1 == subscriptions.length)  {
                console.log('pushing')
                console.log(children)
                container.push(<div className="row" key={"row_" + v4()}>{children}</div>)
                children = []
            }
        })
               
        return container
    }
    
    render() {
        const subscriptions = this.props.subscriptions

        console.log(subscriptions.length)
        return (
            this.populateRows(subscriptions)
        )
    }
}

export default SubscriptionsList