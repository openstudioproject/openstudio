import React, {Component} from "react"
import { v4 } from "uuid"

// import AttendanceListItem from "./ClasscardsListItem"
import Box from '../../../../components/ui/Box'
import BoxBody from '../../../../components/ui/BoxBody'
import ClasscardsListItem from "./ClasscardsListItem";


class ClasscardsList extends Component {
    constructor(props) {
        super(props)
    }

    populateRows = (classcards) => {
        let container = []
        let children = []
        classcards.map((card, i) => {
            console.log(i)
            console.log(card)
            children.push(<ClasscardsListItem key={"card_" + v4()}
                                              data={card} />)
            if (( (i+1) % 3 ) === 0 || i+1 == classcards.length)  {
                console.log('pushing')
                console.log(children)
                container.push(<div className="row" key={"row_" + v4()}>{children}</div>)
                children = []
            }
        })
               
        return container
    }
    
    render() {
        const classcards = this.props.classcards

        console.log(classcards.length)
        return (
            this.populateRows(classcards)
        )
    }
}

export default ClasscardsList