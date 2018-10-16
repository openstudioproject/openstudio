import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl'

// import Check from '../../../components/ui/Check'
// import Label from '../../../components/ui/Label'

import Currency from '../../../components/ui/Currency'


const ProductListItem = injectIntl(withRouter(({data, intl, history}) => 
    <div onClick={() => { history.push('/shop/products/' + data.id) }}
         className="col-md-4">
        <div className="info-box bg-purple">
            <div className="info-box-icon">
                <img src={data.thumblarge} />
            </div>
            <div className="info-box-content">
                <div className="info-box-number">
                    {data.name}
                </div>
                <div className="info-box-text">
                    {data.variants.length} Products
                </div>
            </div>
        </div>
    </div>
))


export default ProductListItem