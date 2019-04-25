import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { injectIntl } from 'react-intl';

import Book from "./Book"
import { appOperations } from '../../duck'
import { classesBookOperations } from './duck'
import { customersListOperations } from  "../../customers/list/duck"
import { shopCartOperations } from '../../shop/cart/duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        options: state.classes.book,
        customer_memberships_today: state.customers.memberships_today,
        school_memberships: state.shop.school.memberships,
        classes: state.classes.classes.data,
    })

const mapDispatchToProps = dispatch =>
    ({        
        checkinCustomer(cuID, clsID, data, history) {
            dispatch(classesBookOperations.checkinCustomer(cuID, clsID, data, history))
        },
        fetchBookingOptions(clsID, cuID) {
            dispatch(classesBookOperations.fetchBookingOptions(clsID, cuID))
        },
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        setPageSubtitle(title) {
            dispatch(appOperations.setPageSubtitle(title))
        },
        setSelectedCustomerID(id) {
            dispatch(customersListOperations.setSelectedCustomerID(id))
        },
        setDisplayCustomerID(id) {
            dispatch(customersListOperations.setDisplayCustomerID(id))
        },
        clearShopCart() {
            dispatch(shopCartOperations.clearItems())
        },
        addShopCartItem(item) {
            dispatch(shopCartOperations.addItem(item))
        }
    })


const BookContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Book)))

export default BookContainer