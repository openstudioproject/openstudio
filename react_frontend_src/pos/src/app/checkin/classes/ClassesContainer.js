import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import Classes from "./ClassesComponent"
import { appOperations } from '../../duck'
import { checkinClassesOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        classes: state.checkin_classes
    })

const mapDispatchToProps = dispatch =>
    ({
        fetchClasses() {
            dispatch(checkinClassesOperations.fetchClasses())
        },
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
    })


const ClassesContainer = injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Classes))

export default ClassesContainer