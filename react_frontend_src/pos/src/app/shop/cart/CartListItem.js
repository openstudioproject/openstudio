import React from "react"
import { injectIntl } from 'react-intl'

// import Check from '../../../components/ui/Check'
// import Label from '../../../components/ui/Label'

import Currency from '../../../components/ui/Currency'
import ClassNameDisplay from '../../../components/ui/ClassNameDisplay'


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


const CartListClassDropin = ({classes, item, selected_item}) => 
    <CartListItemSelected item={item}
                          selected_item={selected_item} >
        {/* <span className="bold">{}</span> <br/> */}

        <div className="bold">
            Drop-in class - <ClassNameDisplay classes={classes}
                                              clsID={item.data.clsID} />         
        </div>
        <CartListItemQuantity qty={item.quantity}
                              price={item.data.Price}
        />
    </CartListItemSelected>


const CartListClassTrial = ({classes, item, selected_item}) => 
    <CartListItemSelected item={item}
                          selected_item={selected_item} >
        {/* <span className="bold">{}</span> <br/> */}
        <div className="bold">
            Trial class - <ClassNameDisplay classes={classes}
                                            clsID={item.data.clsID} />         
        </div>
        <CartListItemQuantity qty={item.quantity}
                              price={item.data.Price}
        />
    </CartListItemSelected>


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


const CartListItem = injectIntl(({classes, item, selected_item, intl, onClick=f=>f}) => 
    <div onClick={() => onClick(item.id)}
         className="shop-cart-list-item">
         { console.log(classes) }
        { (item.item_type == 'class_dropin') ? 
            <CartListClassDropin classes={classes}
                                 item={item}
                                 selected_item={selected_item} /> : '' }
        { (item.item_type == 'class_trial') ? 
            <CartListClassTrial classes={classes}
                                item={item}
                                selected_item={selected_item} /> : '' }
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