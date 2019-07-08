import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"

import Currency from "../../../components/ui/Currency"


class ReconcileLaterClasses extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
    }

    componentWillMount() {
    }

    componentDidMount() {
    }


    render() {
        const data = this.props.data
        console.log('CDRC here')
        console.log(data)
        const classes = data.data.reconcile_later_classes

        return (
           <div>
                { (data.loaded) ?
                    (classes.length) ?
                        <div>     
                            <b>Classes to be paid</b>
                            {classes.map((cls, i) => 
                                <div key={v4()}>
                                    { cls.class_date } {cls.time_start} <br />
                                    <span className="text-muted">
                                        { cls.school_location } { cls.school_classtype } {'( '} <Currency amount={cls.price} /> {')'}
                                    </span>
                                </div>
                            )}
                        </div> : '' 
                : "Loading classes to be reconciled, please wait..."
               }
           </div>
        )
    }
}

export default ReconcileLaterClasses

