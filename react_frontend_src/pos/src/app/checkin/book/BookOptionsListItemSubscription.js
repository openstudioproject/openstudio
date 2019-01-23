import React from "react"
import { injectIntl } from 'react-intl'


import customerHasRequiredMembership from './customerHasRequiredMembership'

const BookOptionsListItemSubscription = injectIntl(({data, customer_memberships, intl, onClick=f=>f}) => 
    <div className="col-md-3"
         onClick={(data.Allowed) ? () => onClick(data): f=>f}>
         {console.log(data)}
         <div className={(data.Allowed) ? "small-box bg-purple" : "small-box bg-gray-active"}>
            <div className="inner">
                <h4>
                    {data.Name}
                </h4>
                <p>
                    {(data.Unlimited) ? "Unlimited" : data.Credits.toFixed(1) + " credits remaining"}
                </p>
            </div>
            <div className="icon">
              <i className="fa fa-pencil-square-o"></i>
            </div>
            { (data.school_memberships_id) ? 
                customerHasRequiredMembership(data.school_memberships_id, customer_memberships) ? 
                    '' : <span className="small-box-footer"><i className="fa fa-exclamation-circle"></i> Membership required - buy now</span> 
                    : ''
            }

            { !(data.Allowed) ?
                <span className="small-box-footer"><i className="fa fa-exclamation-circle"></i> Not allowed for this class</span>
                : '' 
            }
         </div>
    </div>
)

export default BookOptionsListItemSubscription

