import React from "react"
import { v4 } from "uuid"

const RevenueTotal = ({data, currency_symbol}) => 
    <div className="box box-default"> 
        <div className="box-header with-border">
            <h3 className="box-title">Revenue Totals</h3>
        </div>
        <div className="box-body">
            <table className="table">
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Attendance</td>
                        <td>{currency_symbol} { ' ' } {data.total.amount.toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td>Teacher payment</td>
                        <td>{currency_symbol} { ' ' } {data.teacher_payment.amount.toFixed(2)}</td>
                    </tr>
                </tbody>
                <tfoot>
                    <tr>
                        <th>Studio revenue</th>
                        <th>{currency_symbol} { ' ' } {(data.total.amount - data.teacher_payment.amount).toFixed(2)}</th>
                    </tr>
                </tfoot>
            </table>
        </div>
    </div>


export default RevenueTotal