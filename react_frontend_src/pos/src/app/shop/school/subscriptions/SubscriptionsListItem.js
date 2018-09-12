import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl';

import Currency from '../../../../components/ui/Currency'

const representClasses = (data) =>
    data.Classes


const SubscriptionsListItem = injectIntl(withRouter(({data, intl, currency_symbol}) => 
    <div className="col-md-4">
        <div className="panel panel-default">
            <div className="panel-heading">
                <h3 className="panel-title">{data.Name}</h3>
            </div>
                <table className="table table-condensed">
                    <tbody>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.classes" })}</td>
                            <td>{representClasses(data)}</td>
                        </tr>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.monthly" })}</td>
                            <td>{(data.Price) ? 
                                    <Currency amount={data.Price} /> : 
                                    intl.formatMessage({ id:"app.general.strings.not_found"}) }</td>
                        </tr>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.description" })}</td>
                            <td>{data.Description}</td>
                        </tr>
                    </tbody>
                </table>
        </div>
    </div>
))


export default SubscriptionsListItem