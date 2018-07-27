import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import Revenue from "./Revenue"
import { appOperations } from '../../duck'
import { checkinRevenueOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        revenue: state.checkin_revenue
    })

const mapDispatchToProps = dispatch =>
    ({
        fetchRevenue(clsID) {
            dispatch(checkinRevenueOperations.fetchRevenue(clsID))
        },
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
    })


const RevenueContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Revenue)))

export default RevenueContainer