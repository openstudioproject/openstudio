import React from "react"
import { v5 } from "uuid"

import AttendanceListItem from "./AttendanceListItem"

const AttendanceList = ({attendance_items}) => 
    <div className="box box-default">
        <div className="box-body">
            {attendance_items.map((ai) => 
                <AttendanceListItem key={"ai_" + v5()}
                                    data={ai} />
            )}
        </div>
    </div>


export default AttendanceList