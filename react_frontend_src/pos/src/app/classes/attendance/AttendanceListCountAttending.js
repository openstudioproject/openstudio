import React from "react"

// function filterCancelled(attendance_item) {
//     return attendance_item.classes_attendance.BookingStatus != "cancelled"
// }

function filterAttending(attendance_item) {
    return attendance_item.classes_attendance.BookingStatus == "attending"
}

function filterBooked(attendance_item) {
    return attendance_item.classes_attendance.BookingStatus == "booked"
}

function filterCancelled(attendance_item) {
    return attendance_item.classes_attendance.BookingStatus == "booked"
}

// function count_attendance(attendance_items) {
//     let items_not_cancelled = attendance_items.filter(filterCancelled)
//     return items_not_cancelled.length
// }

function count_attending(attendance_items) {
    let items_attending = attendance_items.filter(filterAttending)
    return items_attending.length
}

function count_booked(attendance_items) {
    let items_booked = attendance_items.filter(filterBooked)
    return items_booked.length
}

function count_cancelled(attendance_items) {
    let items_cancelled = attendance_items.filter(filterCancelled)
    return items_cancelled.length
}

const AttendanceListCountAttending = ({attendance_items}) => 
    <div className="box-tools pull-right"> 
        <span className="label label-success">{count_attending(attendance_items)} Attending</span> {" "}
        <span className="label label-primary">{count_booked(attendance_items)} Booked</span> {" "}
        <span className="label label-warning">{count_cancelled(attendance_items)} Cancelled</span>
    </div>


export default AttendanceListCountAttending