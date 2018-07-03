import { connect } from 'react-redux'

import HomeComponent from "./HomeComponent"
import { setLoaderStatus, setLoaderMessage } from "./duck/actions";

console.log('home container here')
const mapStateToProps = state => 
    ({
        home: state.rootReducer.home
    })

const mapDispatchToProps = dispatch =>
    ({
        setLoaderStatus(status) {
            // toDo: move to operations in duck
            dispatch(setLoaderStatus(status))
        },
        setLoaderMessage(message) {
            dispatch(setLoaderMessage(message))
        }
    })

const HomeContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(HomeComponent)

export default HomeContainer