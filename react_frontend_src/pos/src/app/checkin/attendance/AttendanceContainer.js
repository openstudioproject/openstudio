import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import BookingOptions from "./BookingOptionsComponent"
import { appOperations } from '../../duck'
import { checkinBookingOptionsOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
    })

const mapDispatchToProps = dispatch =>
    ({
        fetchClasses() {
            dispatch(checkinBookingOptionsOperations.fetchClasses())
        },
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
    })


const BookingOptionsContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(BookingOptions))

export default BookingOptionsContainer