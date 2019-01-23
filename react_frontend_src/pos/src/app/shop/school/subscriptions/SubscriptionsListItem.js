import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl'

import Currency from '../../../../components/ui/Currency'


const representSubscriptionUnit = ( SubscriptionUnit, intl ) => {
    switch (SubscriptionUnit) {
        case 'week':
            return intl.formatMessage({ id:"app.general.strings.week" })
        case 'month':
            return intl.formatMessage({ id:"app.general.strings.month" })
        default:
            return intl.formatMessage({ id:"app.general.strings.unknown" })
    }
}


const representClasses = (data, intl) => {
    if (data.Unlimited) {
        return intl.formatMessage({ id:"app.general.strings.unlimited" })
    } else {
        return <span>{data.Classes} / {representSubscriptionUnit(data.SubscriptionUnit, intl)}</span>
    }
}
    

const representMembershipRequired = (data, intl) => {
    if (data.MembershipRequired == true) {
        return intl.formatMessage({ id:"app.general.strings.requires_membership" })
    } else {
        return ""
    }
}


const SubscriptionsListItem = injectIntl(withRouter(({data, intl, currency_symbol, onClick=f=>f}) => 
    <div className="col-md-4"
         onClick={onClick}>

        <div className="small-box bg-purple">
            <div className="inner">
                <h4>
                    {data.Name}
                </h4>
                <h4>
                    <b>
                    {(data.Price) ? 
                        <Currency amount={data.Price} /> : 
                    intl.formatMessage({ id:"app.general.strings.not_set"}) }
                    </b> <small className="text-white">per month</small>
                </h4>
                <p>
                    {data.Description}
                </p>
            </div>
            <div className="icon">
              <i className="fa fa-pencil-square-o"></i>
            </div>
            { (data.MembershipRequired == true) ?
                <span className="small-box-footer"><i className="fa fa-exclamation-circle"></i> {representMembershipRequired(data, intl)}</span>
                : ""
            }
         </div>
    </div>
))


export default SubscriptionsListItem
