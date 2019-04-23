import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';

import Classes from "./Classes"
import { appOperations } from '../../duck'
import { classesClassesOperations } from './duck'


const mapStateToProps = state => 
    ({
        app: state.app,
        classes: state.classes.classes
    })

const mapDispatchToProps = dispatch =>
    ({
        fetchClasses() {
            dispatch(classesClassesOperations.fetchClasses())
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