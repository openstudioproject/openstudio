import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
import BankDetails from './BankDetails'


const mapStateToProps = state => 
    ({
        state: state,
        app: state.app,
        selected_customerID: state.customers.list.selectedID
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
    })
    
const BankDetailsContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(BankDetails)))

export default BankDetailsContainer