import React from "react"
import { injectIntl } from 'react-intl'

const BookOptionsListItemSubscription = injectIntl(({data, intl, onClick=f=>f}) => 
    <div className="col-md-3"
         onClick={(data.Allowed) ? () => onClick(data): f=>f}>

        
         
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
            { !(data.Allowed) ?
                <span className="small-box-footer"><i className="fa fa-exclamation-circle"></i> Not allowed for this class</span>
                : '' 
            }
         </div>
    </div>
)

export default BookOptionsListItemSubscription

