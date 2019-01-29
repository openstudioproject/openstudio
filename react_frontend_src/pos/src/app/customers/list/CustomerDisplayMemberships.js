import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"



class CustomerDisplayMemberships extends Component {
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
        const memberships = this.props.memberships

        return (
           <div>
                { (memberships.loaded) ?
                    (memberships.data[customerID]) ?
                        <div>     
                            <b>Memberships</b>
                            {memberships.data[customerID].map((membership, i) => 
                                <div key={v4()}>
                                    { membership.name } <br />
                                    <span className="text-muted">
                                        { membership.start }
                                        { (membership.end) ? " - " + membership.end : ''}
                                    </span>
                                </div>
                            )}
                        </div> : '' 
                : "Loading memberships, please wait..."
               }
               {/* { (memberships.loaded) ?
                <div>
                    <b>Memberships</b>
                    {memberships.data[customerID].map((membership, i) => 
                        <div key={v4()}>
                            { membership.name } <br />
                            <span className="text-muted">
                                { membership.start }
                                { (membership.end) ? " - " + membership.end : ''}
                            </span>
                        </div>
                    )}
                </div>
                : "Loading memberships, please wait..."
               } */}
           </div>
        )
    }
}

export default CustomerDisplayMemberships

