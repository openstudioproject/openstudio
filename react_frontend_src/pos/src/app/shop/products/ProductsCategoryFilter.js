import React, {Component} from "react"
import { v4 } from "uuid"


class ProductsCategoryFilter extends Component {
    constructor(props) {
        super(props)
        console.log(this.props.products)
    }

    render() {
        const products = this.props.products

        return (
            <div className="shop-products-content-products-list">
                {this.populateProducts(products)}
            </div>
        )
    }
}

export default ProductsCategoryFilter

