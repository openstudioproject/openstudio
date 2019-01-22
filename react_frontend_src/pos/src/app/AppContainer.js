import { connect } from 'react-redux'

import App from './App'
import { appOperations } from './duck'
import { customersListOperations } from './customers/list/duck'
import { customersMembershipsTodayOperations } from './customers/memberships_today/duck'
import { shopProductsOperations } from './shop/products/duck'
import { shopSchoolClasscardsOperations } from './shop/school/classcards/duck'
import { shopSchoolMembershipsOperations } from './shop/school/memberships/duck'
import { shopSchoolSubscriptionsOperations } from './shop/school/subscriptions/duck'


const mapStateToProps = state => 
    ({
        app_state: state.app
    })

const mapDispatchToProps = dispatch =>
    ({  
        fetchPaymentMethods() {
            dispatch(appOperations.fetchPaymentMethods())
        },
        fetchProductCategories() {
            dispatch(shopProductsOperations.fetchProductCategories())
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
        fetchCustomersMembershipsToday() {
            dispatch(customersMembershipsTodayOperations.fetchMembershipsToday())
        },
        fetchShopProducts() {
            dispatch(shopProductsOperations.fetchProducts())
        },
        fetchShopSchoolClasscards() {
            dispatch(shopSchoolClasscardsOperations.fetchShopClasscards())
        },
        fetchShopSchoolMemberships() {
            dispatch(shopSchoolMembershipsOperations.fetchShopMemberships())
        },
        fetchShopSchoolSubscriptions() {
            dispatch(shopSchoolSubscriptionsOperations.fetchShopSubscriptions())
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