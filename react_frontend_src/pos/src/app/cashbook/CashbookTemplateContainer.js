import { connect } from 'react-redux'
import { injectIntl } from 'react-intl'
import { withRouter } from 'react-router'

import CashbookTemplate from './CashbookTemplate'
import { appOperations } from '../duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        cashbook: state.cashbook
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
    })


const CashbookTemplateContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(CashbookTemplate)))

export default CashbookTemplateContainer