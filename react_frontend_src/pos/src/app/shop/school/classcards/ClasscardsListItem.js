import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl';

// import Check from '../../../components/ui/Check'
// import Label from '../../../components/ui/Label'

import Currency from '../../../../components/ui/Currency'


const representMembershipRequired = (data, intl) => {
    if (data.MembershipRequired == true) {
        return intl.formatMessage({ id:"app.general.strings.requires_membership" })
    } else {
        return ""
    }
}


const ClasscardsListItem = injectIntl(withRouter(({data, intl, onClick=f=>f}) => 
    <div className="col-md-4"
         onClick={onClick}>
         <div className="small-box bg-purple">
            <div className="inner">
                <p>
                    {data.Name}
                </p>
                <h4>
                    {(data.Price) ? 
                        <Currency amount={data.Price} /> : 
                    intl.formatMessage({ id:"app.general.strings.not_set"}) }
                </h4>
                <p>
                    Valid {data.ValidityDisplay} <br />
                    {data.Description}
                </p>
            </div>
            <div class="icon">
              <i class="fa fa-id-card-o"></i>
            </div>
            { (data.MembershipRequired == true) ?
                <span class="small-box-footer"><i class="fa fa-exclamation-circle"></i> {representMembershipRequired(data, intl)}</span>
                : ""
            }
         </div>
    </div>
))


export default ClasscardsListItem