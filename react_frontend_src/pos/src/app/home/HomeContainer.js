import { connect } from 'react-redux'

import HomeComponent from "./HomeComponent"
import { homeOperations } from '../duck'

const mapStateToProps = state => 
    ({
        app_state: state.root.app
    })

const mapDispatchToProps = dispatch =>
    ({
        setLoading(loading) {
            dispatch(homeOperations.setLoading(loading))
        },
        setLoadingMessage(message) {
            dispatch(homeOperations.setLoadingMessage(message))
        }
    })

const HomeContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(HomeComponent)

export default HomeContainer