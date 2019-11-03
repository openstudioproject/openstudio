import React from "react"
import { injectIntl } from 'react-intl'

import { formatDate } from "../../../utils/date_tools"
import { isoDateStringToDateObject } from "../../../utils/date_tools"
import customerHasRequiredMembership from './customerHasRequiredMembership'
import Currency from '../../../components/ui/Currency'


function getIconClass(data) {
    if (data.Type == "classcard_shop") {
        return "fa fa-shopping-cart"
    } else {
        return "fa fa-pencil-square-o"
    }
}

function getInnerContent(data) {
    if (data.Type == "classcard_shop") {
        return (
            <p>
                <b>Add to cart</b><br />
                Price: <Currency amount={data.Price} /><br />
            </p>
        )
    } else {
        return (
            <p>
               {(data.Unlimited) ? "Unlimited" : data.ClassesRemaining + " Class(es) remaining"}<br />
               Valid until {formatDate(isoDateStringToDateObject(data.Enddate))}
            </p>
        )
    }
}

function getMembershipFooter(data, customer_memberships) {
    if (data.school_memberships_id) {
        if (!customerHasRequiredMembership(data.school_memberships_id, customer_memberships)) {
            if (data.Type == "subscription_shop") {
                return <span className="small-box-footer"><i className="fa fa-plus"></i> Required membership (will also be added to cart)</span> 
            } else {
                return <span className="small-box-footer"><i className="fa fa-exclamation-circle"></i> Membership required - buy now</span> 
            } 
        }
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
                {getInnerContent(data)}
            </div>
            <div className="icon">
              <i className={getIconClass(data)}></i>
            </div>
            { getMembershipFooter(data, customer_memberships) }

            { (!(data.Allowed) && (data.Type === "classcard")) ?
                <span className="small-box-footer"><i className="fa fa-exclamation-circle"></i> Not allowed for this class</span>
                : '' 
            }
         </div>
    </div>
)

export default BookOptionsListItemClasscard

