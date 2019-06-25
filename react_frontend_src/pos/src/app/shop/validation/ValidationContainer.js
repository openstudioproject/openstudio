import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
// import { shopPaymentOperations } from "./duck"
import { shopPaymentOperations } from "../payment/duck"
import { shopCartOperations } from '../cart/duck'
import { customersListOperations } from '../../customers/list/duck'
import { customersClasscardsOperations } from '../../customers/classcards/duck'
import { customersSubscriptionsOperations } from '../../customers/subscriptions/duck'
import { customersMembershipsOperations } from '../../customers/memberships/duck'
import { customersMembershipsTodayOperations } from '../../customers/memberships_today/duck'
import Validation from "./Validation"


const mapStateToProps = state => 
    ({
        state: state,
        app: state.app,
        cart: state.shop.cart,
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
        },
        fetchCustomersClasscards() {
            dispatch(customersClasscardsOperations.fetchClasscards())
        },
        fetchCustomersSubscriptions() {
            dispatch(customersSubscriptionsOperations.fetchSubscriptions())
        },
        fetchCustomersMemberships() {
            dispatch(customersMembershipsOperations.fetchMemberships())
        },
        fetchCustomersMembershipsToday() {
            dispatch(customersMembershipsTodayOperations.fetchMembershipsToday())
        },
    })
    
const ValidationContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Validation)))

export default ValidationContainer