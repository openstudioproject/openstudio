import { connect } from 'react-redux'

import HomeComponent from "./HomeComponent"
import { homeOperations } from '../duck'

const mapStateToProps = state => 
    ({
        app: state.root.app
    })

const mapDispatchToProps = dispatch =>
    ({
        setLoaderStatus(status) {
            dispatch(homeOperations.setLoaderStatus(status))
        },
        setLoaderMessage(message) {
            dispatch(homeOperations.setLoaderMessage(message))
        }
    })

const HomeContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(HomeComponent)

export default HomeContainer