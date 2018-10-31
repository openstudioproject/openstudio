import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import { appOperations } from '../../duck'
import CartTools from './CartTools'


const mapStateToProps = state => 
    ({
        app: state.app
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        }
    })

const CartToolsContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(CartTools))

export default CartToolsContainer