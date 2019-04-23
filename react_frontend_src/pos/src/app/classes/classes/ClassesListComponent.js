import React from "react"
import { v4 } from "uuid"

import ClassesListClass from "./ClassesListClassComponent"

const ClassesList = ({classes}) => 
    <div className="box box-solid">
        <div className="box-header with-border">
            <h3 className="box-title">Please select a class</h3>
        </div>
        <div className="box-body">
            {classes.map((cls) => 
                <ClassesListClass key={"cls_" + v4()}
                                  data={cls} />
            )}
        </div>
    </div>


export default ClassesList