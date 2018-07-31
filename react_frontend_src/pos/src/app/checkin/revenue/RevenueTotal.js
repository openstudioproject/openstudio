import React from "react"

import ButtonVerify from './ButtonVerify'

const RevenueTotal = ({data, intl, currency_symbol}) => 
    <div className="box box-solid"> 
        <div className="box-header with-border">
            <h3 className="box-title">
                {intl.formatMessage({ id:"app.pos.checkin.revenue.total.title" })}
                <small>
                    { ' ' }
                    <i className="text-red fa fa-ban"></i> 
                    { ' ' } {intl.formatMessage({ id:"app.pos.checkin.revenue.total.not_verified" })}
                </small>
            </h3>
            {/* <div className="box-tools pull-right">
                <button className='btn btn-success btn-sm'>
                    Verify
                </button>
            </div> */}
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
                        <td>{currency_symbol} { ' ' } {data.total.amount.toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td>{intl.formatMessage({ id:"app.general.strings.teacher_payment" })}</td>
                        <td>{ (data.teacher_payment.status === 'error') ? 
                                <span className="text-red"> { data.teacher_payment.data } </span> : 
                                currency_symbol +  ' ' + data.teacher_payment.data.Amount.toFixed(2) }
                        </td>
                    </tr>
                </tbody>
                <tfoot>
                    <tr>
                        <th>{intl.formatMessage({ id:"app.pos.checkin.revenue.total.studio_revenue" })}</th>
                        <th>{currency_symbol} { ' ' } { 
                            (data.total.amount - (data.teacher_payment.status === 'error') ?
                                0 : data.teacher_payment.data.Amount).toFixed(2)}
                        </th> 
                    </tr>
                </tfoot>
            </table>
        </div>
        <div className="box-footer">
            <ButtonVerify intl={intl}
                          teacher_payment={data.teacher_payment}
                          onClick={() => console.log('clicked')} />
        </div>
    </div>


export default RevenueTotal