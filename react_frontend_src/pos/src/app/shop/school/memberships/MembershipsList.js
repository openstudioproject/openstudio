import React, {Component} from "react"
import { v4 } from "uuid"

import MembershipsListItem from "./MembershipsListItem";


class MembershipsList extends Component {
    constructor(props) {
        super(props)
    }

    populateRows = (memberships) => {
        let container = []
        let children = []
        memberships.map((membership, i) => {
            children.push(<MembershipsListItem key={"membership_" + v4()}
                                               data={membership}
                                               currency_symbol={this.props.currency_symbol}
                                               onClick={() => this.props.onClick(membership)} />)
            if (( (i+1) % 3 ) === 0 || i+1 == memberships.length)  {
                container.push(<div className="row" key={"row_" + v4()}>{children}</div>)
                children = []
            }
        })
               
        return container
    }
    
    render() {
        const memberships = this.props.memberships

        console.log(memberships.length)
        return (
            this.populateRows(memberships)
        )
    }
}

export default MembershipsList