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

        categories.map( (category, i) => {
            console.log(i)
            console.log(category)

            let activeClass = (i == 0) ? 'active': ''
            let current_id = v4()

            tabs.push(
                <li role="presentation" className={activeClass}>
                    <a href={"#" + current_id} 
                       title={category.description}
                       aria-controls={current_id}
                       role="tab"
                       data-toggle="tab">
                        {category.name}
                    </a>
                </li>
            )

            tabs_content.push(
                <div role="tabpanel" className={"tab-pane " + activeClass} id={current_id}>
                    {category.name}
                </div>
            )

            
        })

        return (
            <div>
                <ul className="nav nav-tabs nav-justified">
                    {tabs}
                </ul>
                <div className="tab-content">
                    {tabs_content}
                </div>
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