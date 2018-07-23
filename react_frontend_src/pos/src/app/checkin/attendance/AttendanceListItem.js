import React from "react"
import { withRouter } from 'react-router-dom'
import { injectIntl } from 'react-intl';

import Check from '../../../components/ui/Check'
import Label from '../../../components/ui/Label'


const bookingStatusLabelClass = (status) => {
    switch (status) {
        case "attending":
            return "label-success"
        case "booked":
            return "label-primary"
        case "cancelled":
            return "label-cancelled"
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


const AttendanceListItem = injectIntl(withRouter(({data, history, intl}) => 
    <div onClick={() => { history.push('/checkin/booking_options/' + data.ClassesID + '/' + data.CustomersID) }}
         className="checkin_attendance_list_item">
        <div className="row">
            <div className="col-md-1">
                <Check color={(data.classes_attendance.BookingStatus == "attending") ? "text-green" : "text-grey"} />
            </div>
            <div className="col-md-2">
                {data.auth_user.display_name}
            </div>
            <div className="col-md-2">
                <Label type={bookingStatusLabelClass(data.classes_attendance.BookingStatus)}>
                    {bookingStatusMessage(data.classes_attendance.BookingStatus, intl)}
                </Label> 
                {' '}
                {(data.classes_reservation.id) ? 
                    <Label type="label-default">
                        {intl.formatMessage({ id: 'app.pos.checkin.attendance.label_enrolled' })}
                    </Label> : ''}
                <br />
                {(data.classes_attendance.CreatedOn)}
            </div>
            <div className="col-md-3">
                {(data.invoices.id) ? "invoice" : "no invoice"}
            </div>
            <div className="col-md-2">

            </div>
            <div className="col-md-2">

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
))


export default AttendanceListItem