import React from "react"
import { injectIntl } from 'react-intl'

import Currency from "../../../components/ui/Currency"

const BookOptionsListItemReconcileLater = injectIntl(({data, intl, onClick=f=>f}) => 
    <div className="col-md-3"
         onClick={() => onClick(data)}>
        <div className="small-box bg-orange">
            <div className="inner">
                <h4>
                    Reconcile later
                </h4>
                <h4>
                    Pay later
                </h4>
                <p>
                    Use this option to check-in a drop-in class that will be paid later
                </p>
            </div>
            <div className="icon">
            <i className="fa fa-clock-o"></i>
            </div>
        </div> 
    </div>
)

export default BookOptionsListItemReconcileLater
