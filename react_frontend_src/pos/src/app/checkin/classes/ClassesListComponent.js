import React from "react"

import ClassesListClass from "./ClassesListClassComponent"

const ClassesList = ({classes}) => 
    <div className="box box-default">
        <div className="box-body">
            {classes.map((cls) => 
                <ClassesListClass key={"cls_" + cls.ClassesID}
                                  data={cls} />
            )}
        </div>
    </div>


export default ClassesList