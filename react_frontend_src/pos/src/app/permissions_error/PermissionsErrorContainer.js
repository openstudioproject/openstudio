import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import PermissionsError from "./PermissionsError"
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


const PermissionsErrorContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(PermissionsError))

export default PermissionsErrorContainer