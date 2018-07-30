import React from "react"
import { v4 } from "uuid"

const RevenueList = ({data, currency_symbol}) => 
    <div className="box box-default"> 
        <div className="box-header with-border">
            <h3 className="box-title">Revenue</h3>
        </div>
        <div className="box-body">
            <table className="table">
                <thead>
                    <tr>
                        <th>Attendance Type</th>
                        <th>Amount</th>
                        <th>Count</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Trial without membership</td>
                        <td>{currency_symbol} { ' ' } {data.trial.no_membership.amount.toFixed(2)}</td>
                        <td>{data.trial.no_membership.count}</td>
                        <td>{currency_symbol} { ' ' } {(data.trial.no_membership.amount * data.trial.no_membership.count).toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td>Trial with membership</td>
                        <td>{currency_symbol} { ' ' } {data.trial.membership.amount.toFixed(2)}</td>
                        <td>{data.trial.membership.count}</td>
                        <td>{currency_symbol} { ' ' } {(data.trial.membership.amount * data.trial.membership.count).toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td>Drop-in without membership</td>
                        <td>{currency_symbol} { ' ' } {data.dropin.no_membership.amount.toFixed(2)}</td>
                        <td>{data.dropin.no_membership.count}</td>
                        <td>{currency_symbol} { ' ' } {(data.dropin.no_membership.amount * data.dropin.no_membership.count).toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td>Drop-in with membership</td>
                        <td>{currency_symbol} { ' ' } {data.dropin.membership.amount.toFixed(2)}</td>
                        <td>{data.dropin.membership.count}</td>
                        <td>{currency_symbol} { ' ' } {(data.dropin.membership.amount * data.dropin.membership.count).toFixed(2)}</td>
                    </tr>
                    { Object.keys(data.classcards).sort().map((key, index) => 
                        <tr key={v4()}>
                            <td>{key}</td>
                            <td>{currency_symbol} { ' ' } {data.classcards[key].amount.toFixed(2)}</td>
                            <td>{data.classcards[key].count}</td>
                            <td>{currency_symbol} { ' ' } {data.classcards[key].total.toFixed(2)}</td>
                        </tr>
                    )}
                    { Object.keys(data.subscriptions).sort().map((key, index) => 
                        <tr key={v4()}>
                            <td>{key}</td>
                            <td>{currency_symbol} { ' ' } {data.subscriptions[key].amount.toFixed(2)}</td>
                            <td>{data.subscriptions[key].count}</td>
                            <td>{currency_symbol} { ' ' } {data.subscriptions[key].total.toFixed(2)}</td>
                        </tr>
                    )}
                           
                </tbody>
                <tfoot>
                    <tr>
                        <th>Total</th>
                        <th></th>
                        <th>{data.total.count}</th>
                        <th>{currency_symbol} { ' ' } {data.total.amount.toFixed(2)}</th>
                    </tr>
                </tfoot>
            </table>
        </div>
    </div>


export default RevenueList