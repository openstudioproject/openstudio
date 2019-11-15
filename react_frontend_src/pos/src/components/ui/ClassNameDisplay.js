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
        console.log('Class data:')
        console.log(class_data)
        console.log("#############")
        return class_data.Teacher + " will teach " + class_data.ClassType + ' in ' + class_data.Location + ' at ' + class_data.Starttime
    } else {
        return "Class info not found"
    }
}

export default ClassNameDisplay