import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import Customers from './Customers'
import { appOperations } from '../../duck'
import { customersOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        customers: state.customers.list
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        clearSearchTimeout() {
            dispatch(customersOperations.clearSearchTimeout())
        },
        setSearchTimeout(timeout) {
            dispatch(customersOperations.setSearchTimeout(timeout))
        }
    })


const CustomersContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Customers)))

export default CustomersContainer