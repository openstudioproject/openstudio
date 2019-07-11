import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
// import { shopPaymentOperations } from "./duck"
import { shopPaymentOperations } from "../payment/duck"
import { shopCartOperations } from '../cart/duck'
import { customersListOperations } from '../../customers/list/duck'
import { customersSchoolInfoOperations } from '../../customers/school_info/duck'
import { customersMembershipsTodayOperations } from '../../customers/memberships_today/duck'
import Validation from "./Validation"


const mapStateToProps = state => 
    ({
        state: state,
        app: state.app,
        cart: state.shop.cart,
        selected_method: state.shop.payment.selectedID,
        selected_customerID: state.customers.list.selectedID
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
        fetchCustomersSchoolInfo(id) {
            dispatch(customersSchoolInfoOperations.fetchSchoolInfo(id))
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