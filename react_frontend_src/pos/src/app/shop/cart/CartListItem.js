import React from "react"
import { injectIntl } from 'react-intl'

// import Check from '../../../components/ui/Check'
// import Label from '../../../components/ui/Label'

import Currency from '../../../components/ui/Currency'


const CartListProduct = ({item}) => 
    <div>
        {console.log('cart item')}
        {console.log(item)}
        <span className="bold">{item.data.variant_name} - {item.data.product_name}</span> <br/>
        <span className="text-muted">{item.quantity}</span>
    </div>


const CartListClasscard = ({item}) => 
    <div>
        {console.log('cart item')}
        {console.log(item)}
        <span className="bold">Classcard - {item.data.Name}</span> <br/>
        <span className="text-muted">{item.quantity}</span>
    </div>


const CartListItem = injectIntl(({item, intl, onClick=f=>f}) => 
    <div>
        { (item.item_type == 'product') ? 
            <CartListProduct item={item} /> : '' }
        { (item.item_type == 'classcard') ?
            <CartListClasscard item={item} /> : '' }
        
        
    </div>
)


export default CartListItem