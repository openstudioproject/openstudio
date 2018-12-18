import React from "react"
import { v4 } from "uuid"
import { injectIntl } from 'react-intl'

const BookOptionsListItemClasscard = injectIntl(({data, intl, onClick=f=>f}) => 
    <div className="col-md-3"
         onClick={onClick}>

        <div className="small-box bg-primary">
            <div className="inner">
                <h4>
                    {data.Name}
                </h4>
                <p>
                    {(data.Unlimited) ? "Unlimited" : data.ClassesRemaining + " Class(es) remaining"}
                </p>
                <p>
                    Valid until {data.Enddate}
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

