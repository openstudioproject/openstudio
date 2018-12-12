import React from "react"
import { withRouter } from 'react-router-dom'

const ClassesListClass = withRouter(({data, history}) => 
    <div onClick={() => { history.push('/checkin/attendance/' + data.ClassesID) }}
         className={(data.Cancelled || data.Holiday) ? "checkin_class cancelled" : "checkin_class"}>
        <div className="row">
            <div className="col-md-1">
                {data.Starttime} 
                { ' - ' }
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

        {/* Move this to button? Don't show button when holiday/cancelled and show description on new line */}
        <div className="row">
            <div className="col-md-12">
                { (data.Cancelled) ? "Cancelled " + data.CancelledDescription : ''}
                { (data.Holiday) ? "Holiday " + data.holidayDescription : ''}
            </div>
        </div>
    </div>
)


export default ClassesListClass