import { connect } from 'react-redux'
import { injectIntl } from 'react-intl'
import { withRouter } from 'react-router'

import ExpensesTemplate from './ExpensesTemplate'
import { appOperations } from '../duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        expenses: state.expenses
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
    })


const ExpensesTemplateContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(ExpensesTemplate)))

export default ExpensesTemplateContainer