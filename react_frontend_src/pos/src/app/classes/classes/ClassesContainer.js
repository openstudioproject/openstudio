import { connect } from 'react-redux'
import { injectIntl } from 'react-intl'
import { withRouter } from "react-router"

import Classes from "./Classes"
import { appOperations } from '../../duck'
import { classesClassesOperations } from "./duck"


const mapStateToProps = state => 
    ({
        app: state.app,
        classes: state.classes.classes
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        setPageSubtitle(title) {
            dispatch(appOperations.setPageSubtitle(title))
        },
        fetchClasses() {
            dispatch(classesClassesOperations.fetchClasses({}))
        },
    })


const ClassesContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Classes)))

export default ClassesContainer