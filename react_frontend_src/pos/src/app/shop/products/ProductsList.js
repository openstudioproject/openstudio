import React, {Component} from "react"
import { v4 } from "uuid"

// import AttendanceListItem from "./ClasscardsListItem"
// import Box from '../../../../components/ui/Box'
// import BoxBody from '../../../../components/ui/BoxBody'
import ProductsListItem from "./ProductsListItem"

class ProductsList extends Component {
    constructor(props) {
        super(props)
        console.log(this.props.products)
    }

    populateProducts = (products) => {
        let container = []
        let children = []

        products.map((product, i) => {
            console.log(i)
            console.log(product)

            // children.push(product.name)
            children.push(
                <ProductsListItem data={product}
                                  key={"product_" + v4()}
                                  onClick={() => this.props.onClick(product)}
                                  />
            )
            if (( (i+1) % 3 ) === 0 || i+1 == products.length)  {
                console.log('pushing')
                console.log(children)
                container.push(<div className="row" key={"row_" + v4()}>{children}</div>)
                children = []
            }
        })
        
        return container
    }

    render() {
        const products = this.props.products

        return (
            this.populateProducts(products)
        )
    }
}

export default ProductsList

