import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router-dom'

import { appOperations } from '../../duck'
import CartToolsCustomer from './CartToolsCustomer'


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

const CartToolsCustomerContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(CartToolsCustomer)))

export default CartToolsCustomerContainer