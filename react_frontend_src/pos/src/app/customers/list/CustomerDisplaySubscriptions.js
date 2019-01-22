import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"



class CustomerDisplaySubscriptions extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
    }

    componentWillMount() {
    }

    componentDidMount() {
    }


    render() {
        const customerID = this.props.customerID
        const subscriptions = this.props.subscriptions

        return (
           <div>
               { (subscriptions.loaded) ?
                (subscriptions.data[customerID]) ?
                    <div>     
                        <b>Subscriptions</b>
                        {subscriptions.data[customerID].map((subscription, i) => 
                            <div key={v4()}>
                                { subscription.name } <br />
                                <span className="text-muted">
                                    { subscription.start }
                                    { (subscription.end) ? " - " + subscription.end : ''}
                                </span>
                            </div>
                        )}
                    </div> : '' 
                : "Loading subscriptions, please wait..."
               }
           </div>
        )
    }
}

export default CustomerDisplaySubscriptions

