import React from "react"
import { injectIntl } from 'react-intl'

// import Check from '../../../components/ui/Check'
// import Label from '../../../components/ui/Label'

import Currency from '../../../components/ui/Currency'


const CartListItemSelected = ({children, item, selected_item}) => 
    (item.id === selected_item) ? 
        <div className="bg-purple text-white">
            {children}
        </div> :
        <div className="">
            {children}
        </div>


const CartListItemQuantity = ({qty, price}) =>
    <span className="text-muted">
        <span className="pull-right"><Currency amount={qty*price} /></span>
        {qty} Item(s) at <Currency amount={price} /> each 
    </span>


const CartListProduct = ({item, selected_item}) => 
    <CartListItemSelected item={item}
                          selected_item={selected_item} >
        {/* <span className="bold">{}</span> <br/> */}
        <div className="bold">{item.data.variant_name} - {item.data.product_name}</div>
        <CartListItemQuantity qty={item.quantity}
                              price={item.data.price}
        />
    </CartListItemSelected>


const CartListClasscard = ({item, selected_item}) => 
    <CartListItemSelected item={item}
                          selected_item={selected_item} >
        <div className="bold">Classcard - {item.data.Name}</div>
        <CartListItemQuantity qty={item.quantity}
                              price={item.data.Price}
        />
    </CartListItemSelected>


const CartListMembership = ({item, selected_item}) => 
    <CartListItemSelected item={item}
                          selected_item={selected_item} >
        <div className="bold">Membership - {item.data.Name}</div>
        <CartListItemQuantity qty={item.quantity}
                              price={item.data.Price}
        />
    </CartListItemSelected>


const CartListSubscription = ({item, selected_item}) => 
    <CartListItemSelected item={item}
                          selected_item={selected_item} >
        <div className="bold">Subscription - {item.data.Name}</div>
        <CartListItemQuantity qty={item.quantity}
                              price={item.data.Price}
        />
    </CartListItemSelected>


const CartListItem = injectIntl(({item, selected_item, intl, onClick=f=>f}) => 
    <div onClick={() => onClick(item.id)}>
        { (item.item_type == 'product') ? 
            <CartListProduct item={item}
                             selected_item={selected_item} /> : '' }
        { (item.item_type == 'classcard') ?
            <CartListClasscard item={item}
                               selected_item={selected_item} /> : '' }
        { (item.item_type == 'membership') ?
            <CartListMembership item={item}
                                selected_item={selected_item} /> : '' }
        { (item.item_type == 'subscription') ?
            <CartListSubscription item={item}
                                  selected_item={selected_item} /> : '' }
    </div>
)


export default CartListItem