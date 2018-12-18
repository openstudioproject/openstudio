import React from "react"
import { v4 } from "uuid"

import BookOptionsListItemClasscard from "./BookOptionsListItemClasscard"
import BookOptionsListItemDropin from "./BookOptionsListItemDropin"
import BookOptionsListItemSubscription from "./BookOptionsListItemSubscription"
import BookOptionsListItemTrial from "./BookOptionsListItemTrial"

const populateRowsSubscriptions = (subscriptions, onClick=f=>f) => {
    let container = []
    let children = []
    subscriptions.map((subscription, i) => {
        children.push(<BookOptionsListItemSubscription key={"subscription_" + v4()}
                                                       data={subscription}
                                                       onClick={() => onClick(subscription)} />)
        if (( (i+1) % 4 ) === 0 || i+1 == subscriptions.length)  {
            container.push(<div className="row" key={"row_" + v4()}>{children}</div>)
            children = []
        }
    })
           
    return container
}

const populateRowsClasscards = (classcards, onClick=f=>f) => {
    let container = []
    let children = []
    classcards.map((classcard, i) => {
        children.push(<BookOptionsListItemClasscard key={"classcard_" + v4()}
                                                       data={classcard}
                                                       onClick={() => onClick(classcard)} />)
        if (( (i+1) % 4 ) === 0 || i+1 == classcards.length)  {
            container.push(<div className="row" key={"row_" + v4()}>{children}</div>)
            children = []
        }
    })
           
    return container
}

const BookOptionsList = ({booking_options, onClick=f=>f}) => 
    <div className="checkin-booking-options">
        {console.log(booking_options)}
        <h4>Subscriptions</h4>
        <div>
            { populateRowsSubscriptions(booking_options.subscriptions, onClick) }
        </div>
        <h4>Class cards</h4>
        <div>
            { populateRowsClasscards(booking_options.classcards, onClick) }
        </div>
        <h4>Drop-in & Trial</h4>
            <div className="row">
                <BookOptionsListItemDropin data={booking_options.dropin}
                                           onClick={onClick} />
                <BookOptionsListItemTrial data={booking_options.trial}
                                          onClick={onClick} />
            </div>
    </div>


export default BookOptionsList