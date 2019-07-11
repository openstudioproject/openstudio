import { connect } from 'react-redux'

import App from './App'
import { appOperations } from './duck'

import { customersListOperations } from './customers/list/duck'


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