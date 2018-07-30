import React from "react"
import { v4 } from "uuid"

const RevenueList = ({data}) => 
    <div className="box box-default"> 
        <div className="box-body">
            <table className="table table-striped">
                <thead>
                    <th>Description</th>
                    <th>Count</th>
                    <th>Amount</th>
                    <th>Total</th>
                </thead>
                <tbody>
                    <tr>
                        <td>Trial without membership</td>
                        <td>{data.trial.no_membership.count}</td>
                        <td>{data.trial.no_membership.amount}</td>
                        <td>{data.trial.no_membership.amount * data.trial.no_membership.count}</td>
                    </tr>
                    <tr>
                        <td>Trial with membership</td>
                        <td>{data.trial.membership.count}</td>
                        <td>{data.trial.membership.count.amount}</td>
                    </tr>
                </tbody>
            </table>
            {/* {data.map((item, i) => 
                {switch (item.key) {
                    case "dropin": 
                        <div>drop in</div>
                    case "trial":
                        <div>trial</div>    
                    case "classcards":
                        <div>classcards</div>    
                    case "subscriptions":
                        <div>subscriptions</div>    
                    case "complementary":
                        <div>complementary</div>    
                    default:
                        ""
                }}
            )} */}
        </div>
    </div>


export default RevenueList