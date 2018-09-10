import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl';

// import Check from '../../../components/ui/Check'
// import Label from '../../../components/ui/Label'

const ClasscardsListItem = injectIntl(withRouter(({data, history, intl}) => 
    <div>{data.Name}</div>
))


export default ClasscardsListItem