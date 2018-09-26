import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl';

const CustomersListItem = injectIntl(({data, history, intl, match, onClick}) => 
    <div className="row" onClick={onClick}>
        {data.display_name}
        Item content!
    </div>
)


export default CustomersListItem