import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router-dom'

// import { appOperations } from '../../duck'
import PaymentMethodName from "./PaymentMethodName"


const mapStateToProps = state => 
    ({
        methods: state.app.payment_methods,
        selected_method: state.shop.payment.selectedID
    })

const mapDispatchToProps = dispatch =>
    ({
        // setPageTitle(title) {
        //     dispatch(appOperations.setPageTitle(title))
        // }
    })

const PaymentMethodNameContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(PaymentMethodName)))

export default PaymentMethodNameContainer