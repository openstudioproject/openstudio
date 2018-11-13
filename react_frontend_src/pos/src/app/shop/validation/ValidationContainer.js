import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
// import { shopPaymentOperations } from "./duck"
import { shopPaymentOperations } from "../payment/duck"
import { shopCartOperations } from '../cart/duck'
import { customersListOperations } from '../../customers/list/duck'
import Validation from "./Validation"


const mapStateToProps = state => 
    ({
        state: state,
        app: state.app,
        items: state.shop.cart.items,
        total: state.shop.cart.total,
        selected_method: state.shop.payment.selectedID
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        clearSelectedPaymentMethod() {
            dispatch(shopPaymentOperations.clearSelectedPaymentMethod())
        },
        clearCartItems() {
            dispatch(shopCartOperations.clearItems())
        },
        clearSelectedCustomer() {
            dispatch(customersListOperations.clearSelectedCustomerID())
        },
        validateCart(state) {
            dispatch(appOperations.validateCart(state))
        }
    })
const ValidationContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Validation)))

export default ValidationContainer