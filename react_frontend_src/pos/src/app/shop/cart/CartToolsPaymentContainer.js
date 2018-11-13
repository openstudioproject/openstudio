import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router-dom'

import { appOperations } from '../../duck'
import CartToolsPayment from './CartToolsPayment'


const mapStateToProps = state => 
    ({
        customers: state.customers.list,
        cart_items: state.shop.cart.items
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        }
    })

const CartToolsPaymentContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(CartToolsPayment)))

export default CartToolsPaymentContainer