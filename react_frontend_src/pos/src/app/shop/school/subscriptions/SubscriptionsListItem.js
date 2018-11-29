import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl';

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
            <div class="icon">
              <i class="fa fa-sign-in"></i>
            </div>
            { (data.MembershipRequired == true) ?
                <span class="small-box-footer"><i class="fa fa-exclamation-circle"></i> {representMembershipRequired(data, intl)}</span>
                : ""
            }
         </div>

        {/* <div className="panel panel-default">
            <div className="panel-heading">
                <h3 className="panel-title">{data.Name}</h3>
            </div>
                <table className="table table-condensed">
                    <tbody>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.classes" })}</td>
                            <td>{representClasses(data, intl)}</td>
                        </tr>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.monthly" })}</td>
                            <td>{(data.Price) ? 
                                    <Currency amount={data.Price} /> : 
                                    intl.formatMessage({ id:"app.general.strings.not_set"}) }</td>
                        </tr>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.pos.products.school.subscription.registration_fee" })}</td>
                            <td>{(data.RegistrationFee) ? 
                                    <Currency amount={data.RegistrationFee} /> : 
                                    intl.formatMessage({ id:"app.general.strings.not_set"}) }</td>
                        </tr>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.description" })}</td>
                            <td>{data.Description}</td>
                        </tr>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.membership" })}</td>
                            <td>{representMembershipRequired(data, intl)}</td>
                        </tr>
                    </tbody>
                </table>
        </div> */}
    </div>
))


export default SubscriptionsListItem
