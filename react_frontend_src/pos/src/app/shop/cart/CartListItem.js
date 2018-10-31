import React from "react"
import { injectIntl } from 'react-intl'

// import Check from '../../../components/ui/Check'
// import Label from '../../../components/ui/Label'

import Currency from '../../../components/ui/Currency'

const CartListItemQuantity = ({qty, price}) =>
    <span className="text-muted">
        {qty} Item(s) at <Currency amount={price} /> each
    </span>


const CartListProduct = ({item}) => 
    <div>
        {console.log('cart item')}
        {console.log(item)}
        <span className="bold">{item.data.variant_name} - {item.data.product_name}</span> <br/>
        <CartListItemQuantity qty={item.quantity}
                              price={item.data.price}
        />
    </div>


const CartListClasscard = ({item}) => 
    <div>
        {console.log('cart item')}
        {console.log(item)}
        <span className="bold">Classcard - {item.data.Name}</span> <br/>
        <CartListItemQuantity qty={item.quantity}
                              price={item.data.Price}
        />
    </div>


const CartListMembership = ({item}) => 
    <div>
        {console.log('cart item')}
        {console.log(item)}
        <span className="bold">Membership - {item.data.Name}</span> <br/>
        <CartListItemQuantity qty={item.quantity}
                              price={item.data.Price}
        />
    </div>


const CartListSubscription = ({item}) => 
    <div>
        {console.log('cart item')}
        {console.log(item)}
        <span className="bold">Subscription - {item.data.Name}</span> <br/>
        <CartListItemQuantity qty={item.quantity}
                              price={item.data.Price}
        />
    </div>


const CartListItem = injectIntl(({item, intl, onClick=f=>f}) => 
    <div>
        { (item.item_type == 'product') ? 
            <CartListProduct item={item} /> : '' }
        { (item.item_type == 'classcard') ?
            <CartListClasscard item={item} /> : '' }
        { (item.item_type == 'membership') ?
            <CartListMembership item={item} /> : '' }
        { (item.item_type == 'subscription') ?
            <CartListSubscription item={item} /> : '' }
        
        
    </div>
)


export default CartListItem