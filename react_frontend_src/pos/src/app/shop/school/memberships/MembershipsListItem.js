import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl';

import Currency from '../../../../components/ui/Currency'


const representValidityUnit = ( Validity, ValidityUnit, intl ) => {
    let unit
    switch (ValidityUnit) {
        case 'day':
            unit = intl.formatMessage({ id:"app.general.strings.day" })
        case 'week':
            unit = intl.formatMessage({ id:"app.general.strings.week" })
        case 'month':
            unit = intl.formatMessage({ id:"app.general.strings.month" })
        default:
            unit = intl.formatMessage({ id:"app.general.strings.unknown" })
    }

    if (Validity != 1) {
        unit = unit + 's'
    }

    return <span>{Validity} {unit}</span>
}


const MembershipsListItem = injectIntl(withRouter(({data, intl, onClick=f=>f}) => 
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
                    </b> <small className="text-white">per {representValidityUnit(data.Validity, data.ValidityUnit, intl)}</small>
                </h4>
                <p>
                    {data.Description}
                </p>
            </div>
            <div className="icon">
              <i className="fa fa-sign-in"></i>
            </div>
         </div>
    </div>
))


export default MembershipsListItem