import { connect } from 'react-redux'
import { injectIntl } from 'react-intl'
import { withRouter } from 'react-router'

import CashCountSet from './CashCountSet'
import { appOperations } from '../duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        cashbook: state.cashbook
    })

const mapDispatchToProps = dispatch =>
    ({
        // setPageTitle(title) {
        //     dispatch(appOperations.setPageTitle(title))
        // },
    })


const CashCountSetContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(CashCountSet)))

export default CashCountSetContainer