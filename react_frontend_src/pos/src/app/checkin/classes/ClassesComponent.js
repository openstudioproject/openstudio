import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import PageTemplate from "../../../components/PageTemplate"

const Class = ({data}) => 
    <div className="row">
        <div className="col-md-1">
            {data.Starttime} -
            {data.Endtime}
        </div>
        <div className="col-md-2">
            {data.Location}
        </div>
        <div className="col-md-2">
            {data.ClassType}
        </div>
        <div className="col-md-3">
            {data.Teacher} { (data.Teacher2) ? ' & ' + data.Teacher2 : ''}
        </div>
        <div className="col-md-2">
            {data.Level}
        </div>
        <div className="col-md-2">
            ({data.MaxStudents - data.CountAttendance})
        </div>
    </div>

// const ClassesList = (classes) => classes.map((cls) => <div>{cls.Location}</div>)
const ClassesList = ({classes}) => 
    <div className="box box-default">
        {/* <div className="box-header with-border">
            <h3 className="box-title">Classes</h3>
        </div> */}
        <div className="box-body">
            {classes.map((cls) => 
                <Class key={"cls_" + cls.ClassesID}
                       data={cls} />
            )}
        </div>
    </div>

class classesComponent extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        fetchClasses: PropTypes.function,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        classes: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.checkin.page_title' })
        )
        this.props.fetchClasses()
        console.log(this.props)
    }

    render() {
        return (
            <PageTemplate app_state={this.props.app}>
                { 
                    (!this.props.classes.loaded) ? 
                        <div>Loading classes, please wait...</div> :
                        <section className="ClassesList">
                            <ClassesList classes={this.props.classes.data} />
                        </section>
                }
            </PageTemplate>
        )
    }
}

export default classesComponent
