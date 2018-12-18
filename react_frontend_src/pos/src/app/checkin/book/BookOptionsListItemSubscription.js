import React from "react"
import { v4 } from "uuid"
import { injectIntl } from 'react-intl'

const BookOptionsListItemSubscription = injectIntl(({data, intl, onClick=f=>f}) => 
    <div className="col-md-3"
         onClick={onClick}>

        <div className="small-box bg-purple">
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
            { !(data.Allowed) ?
                <span className="small-box-footer"><i className="fa fa-exclamation-circle"></i> Not allowed for this class</span>
                : '' 
            }
         </div>
    </div>
)

export default BookOptionsListItemSubscription

