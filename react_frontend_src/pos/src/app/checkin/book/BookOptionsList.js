import React from "react"
import { injectIntl } from 'react-intl'
import { v4 } from "uuid"


import Currency from '../../../components/ui/Currency'

// const BookOptionsListItemSubscription = ({data, onClick=f=>f}) =>
const BookOptionsListItemSubscription = injectIntl(({data, intl, onClick=f=>f}) => 
    <div className="col-md-3"
         onClick={onClick}>

        <div className="small-box bg-purple">
            <div className="inner">
                <h4>
                    {data.Name}
                </h4>
                <p>
                    {(data.Unlimited) ? "Unlimited" : data.Credits.toFixed(1) + " credits remaining"}
                </p>
                {/* <h4>
                    <b>
                    {(data.Price) ? 
                        <Currency amount={data.Price} /> : 
                    intl.formatMessage({ id:"app.general.strings.not_set"}) }
                    </b> <small className="text-white">per month</small>
                </h4> */}
                {/* <p>
                    {data.Description}
                </p> */}
            </div>
            <div className="icon">
              <i className="fa fa-pencil-square-o"></i>
            </div>
            { !(data.Allowed) ?
                <span className="small-box-footer"><i className="fa fa-exclamation-circle"></i> Not allowed for this class</span>
                : '' 
            }
         </div>
    </div>
)

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

const BookOptionsList = ({booking_options, onClick=f=>f}) => 
    <div className="checkin-booking-options">
        {console.log(booking_options)}
        <h4>Subscriptions</h4>
        <div>
            { populateRowsSubscriptions(booking_options.subscriptions) }
            {/* {booking_options.subscriptions.map((item, i) => 
                
                <BookOptionsListItemSubscription key={"booking_item_" + v4()}
                                                 data={item} />
            )} */}
        </div>
    </div>


export default BookOptionsList