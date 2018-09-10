import React from "react"
import { v4 } from "uuid"

// import AttendanceListItem from "./ClasscardsListItem"
import Box from '../../../../components/ui/Box'
import BoxBody from '../../../../components/ui/BoxBody'
import ClasscardsListItem from "./ClasscardsListItem";

const ClasscardsList = ({classcards}) => 
    <Box>
        <BoxBody>
            {console.log(classcards)}
            {classcards.map((card) => 
                <ClasscardsListItem key={"card_" + v4()}
                                    data={card} />
            )}
        </BoxBody>
    </Box>

export default ClasscardsList