import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import Book from "./Book"
import { appOperations } from '../../duck'
import { checkinBookOperations } from './duck'
import { shopCartOperations } from '../../shop/cart/duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        options: state.checkin.book,
        memberships: state.customers.memberships
    })

const mapDispatchToProps = dispatch =>
    ({        
        checkinCustomer(cuID, clsID, data) {
            dispatch(checkinBookOperations.checkinCustomer(cuID, clsID, data))
        },
        fetchBookingOptions(clsID, cuID) {
            dispatch(checkinBookOperations.fetchBookingOptions(clsID, cuID))
        },
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        clearShopCart() {
            dispatch(shopCartOperations.clearItems())
        },
        addShopCartItem(item) {
            dispatch(shopCartOperations.addItem(item))
        }
    })


const BookContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Book))

export default BookContainer