import React from "react"

import ButtonVerify from './ButtonVerify'

const RevenueTotal = ({revenue, teacher_payment, teacher_payment_verifying, intl, currency_symbol,onVerify=f=>f}) => 
    <div className="box box-solid"> 
        {console.log(revenue)}
        {console.log(teacher_payment)}
        <div className="box-header with-border">
            <h3 className="box-title">
                {intl.formatMessage({ id:"app.pos.checkin.revenue.total.title" })}
                <small>
                    { ' ' }
                    { (teacher_payment.data.Status === 'verified') ?
                        // <span>
                        //     <i className="text-green fa fa-check"></i> { ' ' }
                        //     {intl.formatMessage({ id:"app.pos.checkin.revenue.total.verified"})}
                        // </span> 
                        '' :
                        <span>
                            <i className="text-red fa fa-ban"></i> { ' ' }
                            {intl.formatMessage({ id:"app.pos.checkin.revenue.total.not_verified" })}
                        </span>}
                </small>
            </h3>
        </div>
        <div className="box-body">
            <table className="table">
                <thead>
                    <tr>
                        <th>{intl.formatMessage({ id:"app.general.strings.description" })}</th>
                        <th>{intl.formatMessage({ id:"app.general.strings.amount" })}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{intl.formatMessage({ id:"app.general.strings.attendance" })}</td>
                        <td>{currency_symbol} { ' ' } {revenue.total.amount.toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td>{intl.formatMessage({ id:"app.general.strings.teacher_payment" })}</td>
                        <td>{ (teacher_payment.status === 'error') ? 
                                <span className="text-red"> { teacher_payment.data } </span> : 
                                currency_symbol +  ' ' + teacher_payment.data.ClassRate.toFixed(2) }
                        </td>
                    </tr>
                </tbody>
                <tfoot>
                    <tr>
                        <th>{intl.formatMessage({ id:"app.pos.checkin.revenue.total.studio_revenue" })}</th>
                        <th>{currency_symbol} { ' ' } { 
                            (revenue.total.amount - teacher_payment.data.ClassRate).toFixed(2) }
                        </th> 
                    </tr>
                </tfoot>
            </table>
        </div>
        <div className="box-footer">
            <ButtonVerify intl={intl}
                          teacher_payment={teacher_payment}
                          teacher_payment_verifying={teacher_payment_verifying}
                          onClick={onVerify} />
        </div>
    </div>


export default RevenueTotal