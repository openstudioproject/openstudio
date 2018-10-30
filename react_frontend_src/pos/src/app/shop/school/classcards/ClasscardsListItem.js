import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl';

// import Check from '../../../components/ui/Check'
// import Label from '../../../components/ui/Label'

import Currency from '../../../../components/ui/Currency'


const ClasscardsListItem = injectIntl(withRouter(({data, intl, onClick=f=>f}) => 
    <div className="col-md-4"
         onClick={onClick}>
        <div className="panel panel-default">
            <div className="panel-heading">
                <h3 className="panel-title">{data.Name}</h3>
            </div>
                <table className="table table-condensed">
                    <tbody>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.validity" })}</td>
                            <td>{data.ValidityDisplay}</td>
                        </tr>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.classes" })}</td>
                            <td>{data.Classes}</td>
                        </tr>
                        <tr>
                            <td>{intl.formatMessage({ id:"app.general.strings.price" })}</td>
                            <td>
                                {(data.Price) ? 
                                     <Currency amount={data.Price} /> : 
                                     intl.formatMessage({ id:"app.general.strings.not_set"}) }
                            </td>
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


export default ClasscardsListItem