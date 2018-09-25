import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import Customers from './Customers'
import { appOperations } from '../../duck'
import { customersListOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
<<<<<<< HEAD
        barcode_scans: state.app.settings.data.customers_barcodes,
=======
        barcode_scans: state.app.settings.data.checkin_barcodes,
>>>>>>> pos_customers
        customers: state.customers.list
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        clearSearchTimeout() {
            dispatch(customersListOperations.clearSearchTimeout())
        },
        setSearchTimeout(timeout) {
            dispatch(customersListOperations.setSearchTimeout(timeout))
        }
    })


const CustomersContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Customers)))

export default CustomersContainer