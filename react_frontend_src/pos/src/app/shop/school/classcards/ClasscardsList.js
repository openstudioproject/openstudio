import React from "react"
import { v4 } from "uuid"

// import AttendanceListItem from "./ClasscardsListItem"
import Box from '../../../../components/ui/Box'
import BoxBody from '../../../../components/ui/BoxBody'
import ClasscardsListItem from "./ClasscardsListItem";

const ClasscardsList = ({classcards}) => 
    <div>
        {classcards.map((card) => 
            <ClasscardsListItem key={"card_" + v4()}
                                data={card} />
        )}
    </div>

export default ClasscardsList