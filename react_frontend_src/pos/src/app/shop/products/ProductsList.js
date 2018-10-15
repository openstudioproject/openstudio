import React, {Component} from "react"
import { v4 } from "uuid"

// import AttendanceListItem from "./ClasscardsListItem"
// import Box from '../../../../components/ui/Box'
// import BoxBody from '../../../../components/ui/BoxBody'
// import ProductsListItem from "./ProductsListItem"


class ProductsList extends Component {
    constructor(props) {
        super(props)
        console.log(this.props.products)
    }

    populateProducts = (products) => {
        let tabs = []
        let tabs_content = []

        products.map((product, i) => {
            console.log(i)
            console.log(product)
        })
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
        const products = this.props.products

        return (
            <div>
            Products here
            </div>
        )
    }
}

export default ProductsList