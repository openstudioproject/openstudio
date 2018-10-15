import React, {Component} from "react"
import { v4 } from "uuid"

// import AttendanceListItem from "./ClasscardsListItem"
// import Box from '../../../../components/ui/Box'
// import BoxBody from '../../../../components/ui/BoxBody'
// import ProductsListItem from "./ProductsListItem"


class ProductsList extends Component {
    constructor(props) {
        super(props)
        console.log(this.props.categories)
    }

    populateProducts = (categories) => {
        let tabs = []
        let tabs_content = []

        categories.map( (key) => {
            console.log(key)

            // tabs.push(
            //     <li role="presentation" className='active'>
            //         <a href={"#" + v4()}>
            //             tab name here
            //         </a>
            //     </li>
            // )

            
        })

        return (
            <div>
                <ul className="nav nav-tabs">
                    {tabs}
                </ul>
            </div>
        )
    }

    // populateRows = (classcards) => {
    //     let container = []
    //     let children = []
    //     classcards.map((card, i) => {
    //         console.log(i)
    //         console.log(card)
    //         children.push(<ClasscardsListItem key={"card_" + v4()}
    //                                           data={card} />)
    //         if (( (i+1) % 3 ) === 0 || i+1 == classcards.length)  {
    //             console.log('pushing')
    //             console.log(children)
    //             container.push(<div className="row" key={"row_" + v4()}>{children}</div>)
    //             children = []
    //         }
    //     })
               
    //     return container
    // }
    
    render() {
        const categories = this.props.categories

        return (
            this.populateProducts(categories)
        )
    }
}

export default ProductsList