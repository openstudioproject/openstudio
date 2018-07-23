import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import Book from "./Book"
import { appOperations } from '../../duck'
import { checkinBookOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        options: state.checkin_booking_options
    })

const mapDispatchToProps = dispatch =>
    ({
        fetchClassAttendance(clsID) {
            dispatch(checkinBookOperations.fetchBookingOptions(clsID))
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