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
        const data = this.props.data
        const subscriptions = data.data.subscriptions

        return (
           <div>
               { (data.loaded) ?
                (subscriptions.length) ?
                    <div>     
                        <b>Subscriptions</b>
                        {subscriptions.map((subscription, i) => 
                            <div key={v4()}>
                                { subscription.name } <br />
                                <span className="text-muted">
                                    { subscription.start }
                                    { (subscription.end) ? " - " + subscription.end : ''} <br />
                                    Min. until: { subscription.min_end }
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

