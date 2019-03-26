import { connect } from 'react-redux'
import { injectIntl } from 'react-intl'
import { withRouter } from 'react-router'

import Expenses from './Expenses'
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


const ExpensesContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Expenses)))

export default ExpensesContainer