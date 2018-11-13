import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
import { shopPaymentOperations } from "./duck"
import Payment from './Payment'


const mapStateToProps = state => 
    ({
        state: state,
        app: state.app,
        total: state.shop.cart.total,
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
        validateCart(state) {
            dispatch(appOperations.validateCart(state))
        }
    })

const PaymentContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Payment)))

export default PaymentContainer