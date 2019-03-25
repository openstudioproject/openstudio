import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import { v4 } from "uuid"
import { NavLink } from 'react-router-dom'

import PageTemplate from "../../components/PageTemplate"
import Currency from "../../components/ui/Currency"


class ExpensesList extends Component {
    constructor(props) {
        super(props)
        console.log("Expenses list props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        app: PropTypes.object,
        expenses: PropTypes.object,
    }

    componentWillMount() {
    }

    render() {
        const render_items = []
        for (const key of Object.keys(this.props.items)) {
            let item = this.props.items[key]
            render_items.push(item)
        }

        return (
            <div className="box box-solid expenses-list"> 
                <div className="box-header">
                    <h3 className="box-title">
                        <i className="fa fa-book"></i> Today's expenses
                    </h3>
                </div>
                <div className="box-body">

                    {(!render_items.length) ? 'No expensed filed yet': 
                        <div className="expenses-list">
                            {render_items.map((item, i) => 
                                <div className="expensed-list-item" key={v4()} onClick={() => onClick(item.id)}>
                                    <div className="pull-right"><Currency amount={item.amount} /></div>
                                    <div className="bold">{item.description}</div>
                                </div>                       
                            )}
                        </div>
                    }                    
                </div>
            </div>
        )
    }
}

export default ExpensesList
