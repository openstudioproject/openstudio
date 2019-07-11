import React from "react"
import { injectIntl } from 'react-intl'

import Currency from "../../../components/ui/Currency"

const BookOptionsListItemComplementary = injectIntl(({data, intl, onClick=f=>f}) => 
    <div className="col-md-3"
         onClick={() => onClick(data)}>
        <div className="small-box bg-green">
            <div className="inner">
                <h4>
                    Complementary
                </h4>
                <h4>
                    Free
                </h4>
                <p>
                    Use this option to check-in guests
                </p>
            </div>
            <div className="icon">
            <i className="fa fa-user-o"></i>
            </div>
        </div> 
    </div>
)

export default BookOptionsListItemComplementary
