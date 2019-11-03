import React from "react"
import { injectIntl } from 'react-intl'

import { formatDate } from "../../../utils/date_tools"
import { isoDateStringToDateObject } from "../../../utils/date_tools"
import customerHasRequiredMembership from './customerHasRequiredMembership'


function getIconClass(data) {
    if (data.Type == "classcard_shop") {
        return "fa fa-shopping-cart"
    } else {
        return "fa fa-pencil-square-o"
    }
}



function handleOnclick(onClick, data) {
    console.log('hello there!')

    if (data.Type == "classcard") {
        if (data.Allowed) {
            onClick(data)
        } 
    } else {
        onClick(data)
    }
}

const BookOptionsListItemClasscard = injectIntl(({data, customer_memberships, intl, onClick=f=>f}) => 
    <div className="col-md-3"
         onClick={() => handleOnClick(onClick, data)}>
        {console.log('classcard list item')}
        {console.log(data)}
        {console.log(customer_memberships)}
        <div className={(data.Allowed) ? "small-box bg-primary" : "small-box bg-gray-active"}>
            <div className="inner">
                <h4>
                    {data.Name}
                </h4>
                <p>
                    {(data.Unlimited) ? "Unlimited" : data.ClassesRemaining + " Class(es) remaining"}
                </p>
                <p> 
                    Valid until {formatDate(isoDateStringToDateObject(data.Enddate))}
                </p>
            </div>
            <div className="icon">
              <i className={getIconClass(data)}></i>
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

export default BookOptionsListItemClasscard

