import React, {Component} from "react"
import { v4 } from "uuid"

// import AttendanceListItem from "./ClasscardsListItem"
// import Box from '../../../../components/ui/Box'
// import BoxBody from '../../../../components/ui/BoxBody'
import ProductsListItem from "./ProductsListItem"


class ProductsList extends Component {
    constructor(props) {
        super(props)
        console.log(this.props.categories)
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

    populateCategoryProducts = (products) => {
        let container = []
        let children = []

        products.map((product, i) => {
            console.log(i)
            console.log(product)

            // children.push(product.name)
            children.push(
                <ProductsListItem data={product}
                                  key={"product_" + v4()}
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

    populateCategories = (categories) => {
        let tabs = []
        let tabs_content = []

        categories.map( (category, i) => {
            // console.log(i)
            // console.log(category)
            let activeClass = (i == 0) ? 'active': ''
            let current_id = v4()

            tabs.push(
                <li key={v4()} role="presentation" className={activeClass}>
                    <a href={"#" + current_id} 
                       title={category.description}
                       aria-controls={current_id}
                       role="tab"
                       data-toggle="tab"
                       key={v4()}>
                        {category.name}
                    </a>
                </li>
            )

            tabs_content.push(
                <div key={v4()} role="tabpanel" className={"tab-pane " + activeClass} id={current_id}>
                    {/* <h4>{category.description}</h4> */}
                    <br/><br/>
                    {
                        (category.products.length == 0) ? 
                        "No products in this category":
                        this.populateCategoryProducts(category.products)
                    }
                </div>
            )
        })

        return (
            <div>
                <ul className="nav nav-pills nav-justified">
                    {tabs}
                </ul>
                <div className="tab-content">
                    {tabs_content}
                </div>
            </div>
        )
    }

    render() {
        const categories = this.props.categories

        return (
            this.populateCategories(categories)
        )
    }
}

export default ProductsList