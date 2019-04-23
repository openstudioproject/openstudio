import React from "react"
import { withRouter } from 'react-router-dom'

const DisplayCancelled = ({cancelled, description}) => {
    if (cancelled) {
        let cancelled_description = ' '
        if (description) {
            cancelled_description = ' (' + description  + ') '
        }
        return "Cancelled" + cancelled_description
    } else {
        return ''
    }
}

const DisplayHoliday = ({holiday, description}) => {
    if (holiday) {
        let holiday_description = ''
        if (description) {
            holiday_description = ' (' + description  + ')'
        }
        return "Holiday" + holiday_description
    } else {
        return ''
    }
}


function ClassesListClassOnClick(history, data, customerID) {
    if (data.Cancelled || data.Holliday) {
        return () => { console.log('this class is cancelled or in a holiday')}
    } else {
        console.log("on click data")
        console.log(data)
        return () => { history.push('/classes/book/' + customerID + '/' + data.ClassesID) }
    }
}

function ClassesListClassRowClass(data) {
    let cls = 'row '
    if (data.Cancelled || data.Holliday) {
        cls = cls + 'text-muted'
    }
    return cls
}


const ClassesListClass = withRouter(({data, customerID, history}) => 
    <div onClick={ClassesListClassOnClick(history, data, customerID)}
         className={(data.Cancelled || data.Holiday) ? "classes_class cancelled" : "classes_class"}>
        <div className={ClassesListClassRowClass(data)}>
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
        <div className={ClassesListClassRowClass(data)}>
            <div className="col-md-12">
                <DisplayCancelled cancelled={data.Cancelled}
                                  description={data.CancelledDescription} />
                <DisplayHoliday holiday={data.Holiday}
                                description={data.HolidayDescription} />
            </div>
        </div>
    </div>
)


export default ClassesListClass