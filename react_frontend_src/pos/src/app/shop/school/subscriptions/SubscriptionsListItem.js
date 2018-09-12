import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl';

const SubscriptionsListItem = injectIntl(withRouter(({data, intl}) => 
    <div className="col-md-4">
        <div className="panel panel-default">
            <div className="panel-heading">
                <h3 className="panel-title">{data.Name}</h3>
            </div>
                <table className="table table-condensed">
                    <tbody>
                        {/* <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.validity" })}</td>
                            <td>{data.ValidityDisplay}</td>
                        </tr>
                        <tr>
                        <td>{intl.formatMessage({ id:"app.general.strings.classes" })}</td>
                            <td>{data.Classes}</td>
                        </tr>
                        <tr>
                        <td>{intl.formatMessage({ id:"app.general.strings.price" })}</td>
                            <td>{data.Price}</td>
                        </tr>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.description" })}</td>
                            <td>{data.Description}</td>
                        </tr> */}
                    </tbody>
                </table>
        </div>
    </div>
))


export default SubscriptionsListItem