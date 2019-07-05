import { connect } from 'react-redux'

import App from './App'
import { appOperations } from './duck'

import { customersListOperations } from './customers/list/duck'
import { customersMembershipsOperations } from './customers/memberships/duck'
import { customersMembershipsTodayOperations } from './customers/memberships_today/duck'
import { cashbookOperations } from './cashbook/duck'


const mapStateToProps = state => 
    ({
        app_state: state.app
    })

const mapDispatchToProps = dispatch =>
    ({  
        fetchPaymentMethods() {
            dispatch(appOperations.fetchPaymentMethods())
        },
        fetchTaxRates() {
            dispatch(appOperations.fetchTaxRates())
        },
        fetchUser() {
            dispatch(appOperations.fetchUser())
        },
        fetchSettings() {
            dispatch(appOperations.fetchSettings())
        },
        fetchCustomers() {
            dispatch(customersListOperations.fetchCustomers())
        },
        fetchCustomersMemberships() {
            dispatch(customersMembershipsOperations.fetchMemberships())
        },
        fetchCustomersMembershipsToday() {
            dispatch(customersMembershipsTodayOperations.fetchMembershipsToday())
        },
        fetchCashCounts() {
            dispatch(cashbookOperations.fetchCashCounts())
        },
        fetchExpenses() {
            dispatch(cashbookOperations.fetchExpenses())
        },
        setLoaded(loaded) {
            dispatch(appOperations.setLoaded(loaded))
        },
        setLoading(loading) {
            dispatch(appOperations.setLoading(loading))
        },
        setLoadingMessage(message) {
            dispatch(appOperations.setLoadingMessage(message))
        },
        setLoadingProgress(progress) {
            dispatch(appOperations.setLoadingProgress(progress))
        }
    })


const AppContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(App)

export default AppContainer