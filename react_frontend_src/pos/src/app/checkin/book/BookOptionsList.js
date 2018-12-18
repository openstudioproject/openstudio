import React from "react"
import { v4 } from "uuid"


const BookOptionsListItemSubscription = ({data, onClick=f=>f}) =>
    <div>
        {data.Name}
    </div>

const BookOptionsList = ({booking_options, onClick=f=>f}) => 
    <div className="checkin-booking-options">
        {console.log(booking_options)}
        <h4>Subscriptions</h4>
        <div>
            {booking_options.subscriptions.map((item, i) => 
                <BookOptionsListItemSubscription key={"booking_item_" + v4()}
                                                    data={item} />
            )}
        </div>
    </div>


export default BookOptionsList