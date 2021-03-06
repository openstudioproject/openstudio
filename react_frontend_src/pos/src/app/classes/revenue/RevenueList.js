import React from "react"
import { v4 } from "uuid"

const RevenueList = ({revenue, teacher_payment, intl, currency_symbol}) => 
    <div className="box box-solid"> 
        <div className="box-header with-border">
            <h3 className="box-title">{intl.formatMessage({ id:"app.general.strings.revenue" })}</h3>
        </div>
        <div className="box-body">
            {console.log(revenue)}
            <table className="table">
                <thead>
                    <tr>
                        <th>{intl.formatMessage({ id:"app.pos.classes.revenue.list.attendance_type" })}</th>
                        <th>{intl.formatMessage({ id:"app.general.strings.count_customers" })}</th>
                        <th>{intl.formatMessage({ id:"app.general.strings.count_guests" })}</th>
                        <th>{intl.formatMessage({ id:"app.general.strings.attendance" })}</th>
                        <th>{intl.formatMessage({ id:"app.general.strings.amount" })}</th>
                        <th>{intl.formatMessage({ id:"app.general.strings.total" })}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{intl.formatMessage({ id:"app.pos.classes.revenue.list.twom" })}</td>
                        <td>{revenue.trial.no_membership.count}</td>
                        <td>0</td>
                        <td>{revenue.trial.no_membership.count}</td>
                        <td>{currency_symbol} { ' ' } {parseFloat(revenue.trial.no_membership.amount)}</td>
                        <td>{currency_symbol} { ' ' } {(parseFloat(revenue.trial.no_membership.amount) * revenue.trial.no_membership.count)}</td>
                    </tr>
                    <tr>
                        <td>{intl.formatMessage({ id:"app.pos.classes.revenue.list.twm" })}</td>
                        <td>{revenue.trial.membership.count}</td>
                        <td>0</td>
                        <td>{revenue.trial.membership.count}</td>
                        <td>{currency_symbol} { ' ' } {parseFloat(revenue.trial.membership.amount)}</td>
                        <td>{currency_symbol} { ' ' } {(parseFloat(revenue.trial.membership.amount) * revenue.trial.membership.count)}</td>
                    </tr>
                    <tr>
                        <td>{intl.formatMessage({ id:"app.pos.classes.revenue.list.diwm" })}</td>
                        <td>{revenue.dropin.membership.count}</td>
                        <td>0</td>
                        <td>{revenue.dropin.membership.count}</td>
                        <td>{currency_symbol} { ' ' } {parseFloat(revenue.dropin.membership.amount)}</td>
                        <td>{currency_symbol} { ' ' } {(parseFloat(revenue.dropin.membership.amount) * revenue.dropin.membership.count)}</td>
                    </tr>
                    <tr>
                        <td>{intl.formatMessage({ id:"app.pos.classes.revenue.list.diwom" })}</td>
                        <td>{revenue.dropin.no_membership.count}</td>
                        <td>0</td>
                        <td>{revenue.dropin.no_membership.count}</td>
                        <td>{currency_symbol} { ' ' } {parseFloat(revenue.dropin.no_membership.amount)}</td>
                        <td>{currency_symbol} { ' ' } {(parseFloat(revenue.dropin.no_membership.amount) * revenue.dropin.no_membership.count)}</td>
                    </tr>
                    { Object.keys(revenue.subscriptions).sort().map((key, index) => 
                        <tr key={v4()}>
                            <td>{key}</td>
                            <td>{revenue.subscriptions[key].count}</td>
                            <td>0</td>
                            <td>{revenue.subscriptions[key].count}</td>
                            <td>{currency_symbol} { ' ' } {parseFloat(revenue.subscriptions[key].amount)}</td>
                            <td>{currency_symbol} { ' ' } {revenue.subscriptions[key].total}</td>
                        </tr>
                    )}
                    { Object.keys(revenue.staff_subscriptions).sort().map((key, index) => 
                        <tr key={v4()}>
                            <td>{key}</td>
                            <td>0</td>
                            <td>{revenue.staff_subscriptions[key].count}</td>
                            <td>{revenue.staff_subscriptions[key].count}</td>
                            <td>{currency_symbol} { ' ' } {parseFloat(revenue.staff_subscriptions[key].amount)}</td>
                            <td>{currency_symbol} { ' ' } {revenue.staff_subscriptions[key].total}</td>
                        </tr>
                    )}
                    { Object.keys(revenue.classcards).sort().map((key, index) => 
                        <tr key={v4()}>
                            <td>{key}</td>
                            <td>{revenue.classcards[key].count}</td>
                            <td>0</td>
                            <td>{revenue.classcards[key].count}</td>
                            <td>{currency_symbol} { ' ' } {parseFloat(revenue.classcards[key].amount)}</td>
                            <td>{currency_symbol} { ' ' } {revenue.classcards[key].total}</td>
                        </tr>
                    )}
                    {/* Complementary */}
                    <tr>
                        <td>{intl.formatMessage({ id:"app.pos.classes.revenue.list.complementary" })}</td>
                        <td>0</td>
                        <td>{revenue.complementary.count}</td>
                        <td>{revenue.complementary.count}</td>
                        <td>{currency_symbol} { ' ' } {parseFloat(revenue.complementary.amount)}</td>
                        <td>{currency_symbol} { ' ' } {(0)}</td>
                    </tr>
                    {/* Reconcile later */}
                    <tr>
                        <td>{intl.formatMessage({ id:"app.pos.classes.revenue.list.reconcile_later" })}</td>
                        <td>{revenue.reconcile_later.count}</td>
                        <td>0</td>
                        <td>{revenue.reconcile_later.count}</td>
                        <td>{currency_symbol} { ' ' } {parseFloat(revenue.reconcile_later.amount)}</td>
                        <td>{currency_symbol} { ' ' } {(0)}</td>
                        
                    </tr>
                           
                </tbody>
                <tfoot>
                    <tr>
                        <th>{intl.formatMessage({ id:"app.general.strings.total" })}</th>
                        <th>{revenue.total.count_paid}</th>
                        <th>{revenue.total.count_unpaid}</th>
                        <th>{revenue.total.count_total}</th>
                        <th></th>
                        <th>{currency_symbol} { ' ' } {parseFloat(revenue.total.amount)}</th>
                    </tr>
                </tfoot>
            </table>
        </div>
    </div>


export default RevenueList