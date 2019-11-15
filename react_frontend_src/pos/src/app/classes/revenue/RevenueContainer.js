import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import Revenue from "./Revenue"
import { appOperations } from '../../duck'
import { classesRevenueOperations } from './duck'
import { classesClassesOperations } from "../classes/duck"


const mapStateToProps = state => 
    ({
        app: state.app,
        data: state.classes.revenue,
        settings: state.app.settings.data,
        classes: state.classes.classes,
    })

const mapDispatchToProps = dispatch =>
    ({
        fetchRevenueAndTeacherPayment(clsID) {
            dispatch(classesRevenueOperations.fetchRevenueAndTeacherPayment(clsID))
        },
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        },
        verifyTeacherPayment(tpcID) {
            dispatch(classesRevenueOperations.verifyTeacherPayment(tpcID))
        },
        fetchClasses(obj) {
            dispatch(classesClassesOperations.fetchClasses(obj))
        },
    })


const RevenueContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Revenue)))

export default RevenueContainer