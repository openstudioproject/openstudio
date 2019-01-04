import React from "react"
import { v4 } from "uuid"

import AttendanceListItem from "./AttendanceListItem"
import Label from '../../../components/ui/Label'

const bookingStatusLabelClass = (status) => {
    switch (status) {
        case "attending":
            return "label-success"
        case "booked":
            return "label-primary"
        case "cancelled":
            return "label-warning"
    }
}

const bookingStatusMessage = (status, intl) => {
    switch (status) {
        case "attending":
            return intl.formatMessage({ id: 'app.pos.checkin.attendance.status.attending' })
        case "booked":
            return intl.formatMessage({ id: 'app.pos.checkin.attendance.status.booked' })
        case "cancelled":
            return intl.formatMessage({ id: 'app.pos.checkin.attendance.status.cancelled' })
    }
}


const AttendanceList = ({attendance_items, intl, title="", onClick=f=>f}) => 
    <div className="box box-default"> 
        <div className="box-header">
            <h3 className="box-title">{title}</h3>
        </div>
        <div className="box-body">
            <table className="table table-striped table-hover">
                    <thead>
                        <tr>
                            <th></th>
                            <th>Customer</th>
                            <th>Check-in status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {attendance_items.map((item, i) => 
                            <tr key={v4()} onClick={() => onClick(item.classes_attendance.id)}>
                                {console.log(item)}
                                {console.log(item.auth_user.thumbsmall)}
                                <td className="customers_list_image"><img src={item.auth_user.thumbsmall}></img></td>
                                <td>{item.auth_user.display_name}</td>
                                <td><Label type={bookingStatusLabelClass(item.classes_attendance.BookingStatus)}>
                                        {bookingStatusMessage(item.classes_attendance.BookingStatus, intl)}
                                    </Label> 
                                    {' '}
                                    {(item.classes_reservation.id) ? 
                                        <Label type="label-default">
                                            {intl.formatMessage({ id: 'app.pos.checkin.attendance.label_enrolled' })}
                                        </Label> : ''}
                                    <br />
                                    <span className="text-muted"><small>{(item.classes_attendance.CreatedOn)}</small></span>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            {/* {attendance_items.map((ai, i) => 
                <AttendanceListItem key={"ai_" + v4()}
                                    data={ai} />
            )} */}
        </div>
    </div>


export default AttendanceList