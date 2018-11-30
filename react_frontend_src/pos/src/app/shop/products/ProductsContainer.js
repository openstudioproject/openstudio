import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
import { shopCartOperations } from '../cart/duck'
import { customersListOperations } from '../../customers/list/duck'
import Products from './Products'


const mapStateToProps = state => 
    ({
        app: state.app,
        loaded: state.shop.products.loaded,
        products: state.shop.products.data
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
        }
    })

const ProductsContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Products)))

export default ProductsContainer