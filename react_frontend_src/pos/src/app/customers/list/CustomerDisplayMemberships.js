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
        const data = this.props.data
        console.log('CDM here')
        console.log(data)
        const memberships = data.data.memberships

        return (
           <div>
                { (data.loaded) ?
                    (memberships.length) ?
                        <div>     
                            <b>Memberships</b>
                            {memberships.map((membership, i) => 
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

