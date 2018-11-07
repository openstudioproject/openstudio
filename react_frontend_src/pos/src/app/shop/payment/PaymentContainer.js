import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
import { shopPaymentOperations } from "./duck"
import Payment from './Payment'


const mapStateToProps = state => 
    ({
        app: state.app,
        total: state.shop.cart.total,
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        setSelectedPaymentMethod(id) {
            dispatch(shopPaymentOperations.setSelectedPaymentMethod(id))
        }
    })

const PaymentContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Payment)))

export default PaymentContainer