import { connect } from 'react-redux'
import { injectIntl } from 'react-intl'
import { withRouter } from 'react-router'

import ExpenseAdd from './ExpenseAdd'
import { cashbookOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        cashbook: state.cashbook,
        error_data: state.cashbook.expense_update_error_data
    })

const mapDispatchToProps = dispatch =>
    ({
        createExpense(data, history) {
            dispatch(cashbookOperations.createExpense(data, history))
        },
    })


const ExpenseEditContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(ExpenseAdd)))

export default ExpenseEditContainer