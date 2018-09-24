import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import Customers from './Customers'
import { appOperations } from '../duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        customers: state.customers
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        // clearCheckinSearchTimeout() {
        //     dispatch(checkinAttendanceOperations.clearCheckinSearchTimeout())
        // },
        // setCheckinSearchTimeout(timeout) {
        //     dispatch(checkinAttendanceOperations.setCheckinSearchTimeout(timeout))
        // }
    })


const CustomersContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Customers)))

export default CustomersContainer