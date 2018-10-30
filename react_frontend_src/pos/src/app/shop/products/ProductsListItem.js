import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl'

// import Check from '../../../components/ui/Check'
// import Label from '../../../components/ui/Label'

import Currency from '../../../components/ui/Currency'


const ProductListItem = injectIntl(({data, intl, onClick=f=>f}) => 
    <div onClick={onClick}
         className="col-md-4">
        <div className="info-box bg-purple">
            <div className="info-box-icon">
                <img src={data.thumblarge} />
            </div>
            <div className="info-box-content">
                <div className="info-box-text">
                    {data.product_name}
                </div>
                <div className="info-box-number">
                    {data.variant_name} {' '}
                </div>
                <div className="info-box-text">
                    { (data.price) ? 
                      <Currency amount={data.price} /> : 
                      intl.formatMessage({ id:"app.general.strings.not_set"}) }
                </div>
            </div>
        </div>
    </div>
)


export default ProductListItem