import React from "react"
import { injectIntl } from 'react-intl'

import Currency from "../../../components/ui/Currency"

import customerHasRequiredMembership from './customerHasRequiredMembership'


function getMembershipFooter(data, customer_memberships) {
    if (data.school_memberships_id) {
        if (!customerHasRequiredMembership(data.school_memberships_id, customer_memberships)) {
            if (data.Type == "dropin_and_membership") {
                return <span className="small-box-footer"><i className="fa fa-plus"></i> Required membership (will be added to cart)</span> 
            }
        }
    }    
}


const BookOptionsListItemDropin = injectIntl(({data, intl, customer_memberships, onClick=f=>f}) => 
    <div className="col-md-3"
         onClick={() => onClick(data)}>
        {(data.Price) ?
            <div className="small-box bg-aqua-active">
                <div className="inner">
                    <h4>
                        Drop-in class
                    </h4>
                    <h4>
                        <Currency amount={data.Price} />
                    </h4>
                    <p>
                        {
                            (data.MembershipPrice) ? "Membership price" : "Non membership price"
                        }
                    </p>
                    <p>
                        {data.Message}
                    </p>
                </div>
                <div className="icon">
                <i className="fa fa-shopping-cart"></i>
                </div>
                { getMembershipFooter(data, customer_memberships) }
            </div>
            : "Drop-in class price not set for this class"
        }
    </div>
)

export default BookOptionsListItemDropin

