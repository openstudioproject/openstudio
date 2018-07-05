import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import HomeComponent from "./HomeComponent"
import { homeOperations } from '../duck'


const mapStateToProps = state => 
    ({
        app_state: state.root.app
    })

const mapDispatchToProps = dispatch =>
    ({
        setLoadingMessage(message) {
            dispatch(homeOperations.setLoadingMessage(message))
        }
    })


const HomeContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(HomeComponent))

export default HomeContainer