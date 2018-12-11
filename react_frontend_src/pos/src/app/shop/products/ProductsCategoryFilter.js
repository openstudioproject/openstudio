import React, {Component} from "react"
import { v4 } from "uuid"


class ProductsCategoryFilter extends Component {
    constructor(props) {
        super(props)
        console.log(this.props.categories)
    }

    render() {
        const categories = this.props.categories

        return (
            <nav className="navbar navbar-default">
                <div className="container-fluid">
                    <div className="navbar-right">
                        <p className="navbar-text">Product categories</p>
                    </div>
                    <ul className="nav navbar-nav">
                        { categories.map((category, i) => 
                            <li role="presentation" 
                                key={v4()}
                                onClick={() => this.props.onClick(category.id)}>
                                <a href="#" onClick={(e) => e.preventDefault()}>{category.Name}</a>
                            </li>
                        )}
                    </ul>
                </div>
            </nav>
            // <ul className="nav nav-pills nav-justified shop-products-content-categories">
            //     { categories.map((category, i) => 
            //         <li role="presentation" onClick={this.props.onClick}>
            //             <a href="#">{category.Name}</a>
            //         </li>
            //     )}
            // </ul>
        )
    }
}

export default ProductsCategoryFilter

