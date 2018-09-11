import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl';

// import Check from '../../../components/ui/Check'
// import Label from '../../../components/ui/Label'

const ClasscardsListItem = injectIntl(withRouter(({data, index}) => 
    <div className="col-md-4">
        <div className="panel panel-default">
            <div className="panel-heading">
                <h3 className="panel-title">{data.Name}</h3>
            </div>
                <table className="table table-condensed">
                    <tbody>
                        <tr>
                            <td>Validity</td>
                            <td>{data.ValidityDisplay}</td>
                        </tr>
                        <tr>
                            <td>Classes</td>
                            <td>{data.Classes}</td>
                        </tr>
                        <tr>
                            <td>Price</td>
                            <td>{data.Price}</td>
                        </tr>
                        <tr>
                            <td>Description</td>
                            <td>{data.Description}</td>
                        </tr>
                    </tbody>
                </table>
        </div>
    </div>
))


export default ClasscardsListItem