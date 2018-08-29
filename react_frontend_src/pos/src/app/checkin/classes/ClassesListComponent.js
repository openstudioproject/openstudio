import React from "react"
import { v4 } from "uuid"

import ClassesListClass from "./ClassesListClassComponent"

const ClassesList = ({classes}) => 
    <div className="box box-default">
        <div className="box-body">
            {classes.map((cls) => 
                <ClassesListClass key={"cls_" + v4()}
                                  data={cls} />
            )}
        </div>
    </div>


export default ClassesList