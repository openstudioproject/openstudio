import { connect } from 'react-redux'
import { injectIntl } from 'react-intl'
import { withRouter } from 'react-router'

import ExpenseEdit from './ExpenseEdit'
import { cashbookOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        cashbook: state.cashbook,
        error_data: state.cashbook.expense_update_error_data
    })

const mapDispatchToProps = dispatch =>
    ({
        updateExpense(id, data, history) {
            dispatch(cashbookOperations.updateExpense(id, data, history))
        },
    })


const ExpenseEditContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(ExpenseEdit)))

export default ExpenseEditContainer