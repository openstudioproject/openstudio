import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router-dom'

import { appOperations } from '../../duck'
import CustomerButton from './CustomerButton'


const mapStateToProps = state => 
    ({
        customers: state.customers.list
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        }
    })

const CustomerButtonContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(CustomerButton)))

export default CustomerButtonContainer