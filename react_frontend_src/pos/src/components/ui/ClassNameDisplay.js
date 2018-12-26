import React from "react"


const ClassNameDisplay = ({classes, clsID}) => {
    var i
    var class_data
    for (i = 0; i < classes.length; i++) { 
        if ( classes[i].ClassesID == clsID) {
            class_data = classes[i]
            break
        }
    }

    if (class_data) {
        return class_data.ClassType + ' in ' + class_data.Location + ' @' + class_data.Starttime
    } else {
        return "Class info not found"
    }
}

export default ClassNameDisplay