import React from "react"
import { v4 } from "uuid"


function filterAttending(attendance_item) {
  return attendance_item.classes_attendance.BookingStatus == "attending"
}

function count_attending(attendance_items) {
  let items_attending = attendance_items.filter(filterAttending)
  return items_attending.length
}

function get_class_spaces(classes, clsID) {
  var i
  var class_data

  for (i = 0; i < classes.length; i++) { 
      if ( classes[i].ClassesID == clsID) {
          class_data = classes[i]
          break
      }
  }
  if (class_data) {
    return class_data.MaxStudents
  }
}

function over_spaces(attendance_items, classes, clsID) {
  const spacesTotal = get_class_spaces(classes, clsID)
  const countAttending = count_attending(attendance_items)

  // console.log("##########")
  // console.log(spacesTotal)
  // console.log(countAttending)

  if (countAttending >= spacesTotal) {
    return true
  } else {
    return false
  }
}

const AttendanceWarningFull = ({attendance_items, classes, clsID, intl}) => 
  <div className="row">
    <div className="col-md-12">
      {
        (over_spaces(attendance_items, classes, clsID) ? 
          <div class="alert alert-success" role="alert">
            <i className="fa fa-check"></i> {" "}
            This class is full. All {get_class_spaces(classes, clsID)} spaces are filled.
          </div>
          : "")
      }
    </div>
  </div>

export default AttendanceWarningFull