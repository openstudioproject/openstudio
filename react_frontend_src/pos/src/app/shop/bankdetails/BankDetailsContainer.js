import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
import BankDetails from './BankDetails'


const mapStateToProps = state => 
    ({
        state: state,
        app: state.app,
        selected_customerID: state.customers.list.selectedID,
        customers: state.customers.list.data
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        setPageSubtitle(subtitle) {
            dispatch(appOperations.setPageSubtitle(subtitle))
        },
    })
    
const BankDetailsContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(BankDetails)))

export default BankDetailsContainer