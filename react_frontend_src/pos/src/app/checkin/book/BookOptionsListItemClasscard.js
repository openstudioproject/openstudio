import React from "react"
import { injectIntl } from 'react-intl'

import { formatDate } from "../../../utils/date_tools"
import { isoDateStringToDateObject } from "../../../utils/date_tools"


const BookOptionsListItemClasscard = injectIntl(({data, intl, onClick=f=>f}) => 
    <div className="col-md-3"
         onClick={() => onClick(data)}>

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
              <i className="fa fa-id-card-o"></i>
            </div>
            { !(data.Allowed) ?
                <span className="small-box-footer"><i className="fa fa-exclamation-circle"></i> Not allowed for this class</span>
                : '' 
            }
         </div>
    </div>
)

export default BookOptionsListItemClasscard

