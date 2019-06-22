import React from "react"

function filterCancelled(attendance_item) {
    return attendance_item.classes_attendance.BookingStatus != "cancelled"
}


function count_attendance(attendance_items) {
    let items_not_cancelled = attendance_items.filter(filterCancelled)
    return items_not_cancelled.length
}


const AttendanceListCountAttending = ({attendance_items}) => 
    <div className="box-tools pull-right"> 
        Total attending: {count_attendance(attendance_items)}
    </div>


export default AttendanceListCountAttending