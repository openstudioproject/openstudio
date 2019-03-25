import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { NavLink } from 'react-router-dom'

import PageTemplate from "../../components/PageTemplate"


class Expenses extends Component {
    constructor(props) {
        super(props)
        console.log("Expenses props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        app: PropTypes.object,
    }

    componentWillMount() {
    }

    render() {


        return (
            <div className="box box-solid expenses-list"> 
            <div className="box-header">
                <h3 className="box-title">
                    Today's expenses
                </h3>
            </div>
            <div className="box-body">
                test
            {/* {(items.length) ? 
                // <CartList classes={classes}
                //           items={items}
                //           selected_item={selected_item}
                //           total={total}
                //           onClick={this.onClickCartItem.bind(this)} />:
            // "The shopping cart is empty" } */}
            </div> 
        </div> 
        )
    }
}

export default Expenses
