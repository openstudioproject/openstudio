import { connect } from 'react-redux'

import App from './App'
import { appOperations } from './duck'
import { shopSchoolClasscardsOperations } from './shop/school/classcards/duck'
import { shopSchoolSubscriptionsOperations } from './shop/school/subscriptions/duck'


const mapStateToProps = state => 
    ({
        app_state: state.app
    })

const mapDispatchToProps = dispatch =>
    ({  
        fetchUser() {
            dispatch(appOperations.fetchUser())
        },
        fetchSettings() {
            dispatch(appOperations.fetchSettings())
        },
        fetchShopSchoolClasscards() {
            dispatch(shopSchoolClasscardsOperations.fetchShopClasscards())
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