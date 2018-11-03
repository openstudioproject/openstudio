import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import { appOperations } from '../../duck'
import { shopCartOperations } from "./duck"
import CartTools from './CartTools'


const mapStateToProps = state => 
    ({
        customers: state.customers.list,
        cart_selected_item: state.shop.cart.selected_item
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        deleteSelectedItem(id) {
            dispatch(shopCartOperations.deleteSelectedItem(id))
        },
    })

const CartToolsContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(CartTools))

export default CartToolsContainer