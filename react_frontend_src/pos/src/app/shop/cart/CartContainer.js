import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import { appOperations } from '../../duck'
import { shopCartOperations } from './duck'
import Cart from './Cart'


const mapStateToProps = state => 
    ({
        app: state.app,
        checkin_classes: state.checkin.classes.data,
        items: state.shop.cart.items,
        selected_item: state.shop.cart.selected_item,
        total: state.shop.cart.total
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