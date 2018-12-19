import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import Book from "./Book"
import { appOperations } from '../../duck'
import { checkinBookOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        options: state.checkin.book
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
    })


const BookContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Book))

export default BookContainer