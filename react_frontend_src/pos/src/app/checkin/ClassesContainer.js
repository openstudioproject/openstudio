import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import Classes from "./ClassesComponent"
import { appOperations } from '../duck'


const mapStateToProps = state => 
    ({
        app: state.app
    })

const mapDispatchToProps = dispatch =>
    ({
        setLoadingMessage(message) {
            dispatch(appOperations.setLoadingMessage(message))
        },
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        }
    })


const ClassesContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(ClassesComponent))

export default ClassesContainer