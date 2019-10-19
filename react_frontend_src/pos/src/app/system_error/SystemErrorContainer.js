import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import SystemError from "./SystemErrorComponent"
import { appOperations } from '../duck'


const mapStateToProps = state => 
    ({
        app_state: state.app
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


const SystemErrorContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(SystemError))

export default SystemErrorContainer