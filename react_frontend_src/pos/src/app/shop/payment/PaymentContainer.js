import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
import { shopPaymentOperations } from "./duck"
import { customersListOperations } from '../../customers/list/duck'
import Payment from './Payment'


const mapStateToProps = state => 
    ({
        app: state.app,
        total: state.shop.cart.total,
        items: state.shop.cart.items,
        selected_method: state.shop.payment.selectedID
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        setSelectedPaymentMethod(id) {
            dispatch(shopPaymentOperations.setSelectedPaymentMethod(id))
        },
        setCustomersListRedirectNext(next) {
            dispatch(customersListOperations.setRedirectNextComponent(next))
        }
    })

const PaymentContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Payment)))

export default PaymentContainer