import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../../duck'
import Classcards from './Classcards'


const mapStateToProps = state => 
    ({
        app: state.app,
        loaded: state.shop.school.classcards.loaded,
        classcards: state.shop.school.classcards.data
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        }
    })

const ClasscardsContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Classcards)))

export default ClasscardsContainer