import React from "react"
import { injectIntl } from 'react-intl'

import Currency from "../../../components/ui/Currency"

const BookOptionsListItemTrial = injectIntl(({data, intl, onClick=f=>f}) => 
    <div className="col-md-3"
         onClick={() => onClick(data)}>

        <div className="small-box bg-green">
            <div className="inner">
                <h4>
                    Trial class
                </h4>
                <h4>
                    <Currency amount={data.Price} />
                </h4>
                <p>
                    {data.Message}
                </p>
            </div>
            <div className="icon">
              <i className="fa fa-id-card-o"></i>
            </div>
         </div>
    </div>
)

export default BookOptionsListItemTrial
