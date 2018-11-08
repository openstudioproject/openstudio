import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
// import { shopPaymentOperations } from "./duck"
import Validation from "./Validation"


const mapStateToProps = state => 
    ({
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
    })

const ValidationContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Validation)))

export default ValidationContainer