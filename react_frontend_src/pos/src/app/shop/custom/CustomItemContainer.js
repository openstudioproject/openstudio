import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
import { shopCartOperations } from '../cart/duck'
// import { shopProductsOperations } from './duck'
import { customersListOperations } from '../../customers/list/duck'

import CustomItem from './CustomItem'


const mapStateToProps = state => 
    ({
        app: state.app,
        loaded: state.shop.products.loaded,
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        addToCart(item) {
            dispatch(shopCartOperations.addItem(item))
        },
        setCustomersListRedirectNext(next) {
            dispatch(customersListOperations.setRedirectNextComponent(next))
        },

    })

const CustomItemContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(CustomItem)))

export default CustomItemContainer