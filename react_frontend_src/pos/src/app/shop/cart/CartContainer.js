import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import { appOperations } from '../../duck'
import { shopCartOperations } from './duck'
import Cart from './Cart'


const mapStateToProps = state => 
    ({
        app: state.app,
        items: state.shop.cart.items
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        setSelectedItem(id) {
            dispatch(shopCartOperations.setSelectedItem(id))
        }
    })

const CartContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Cart))

export default CartContainer