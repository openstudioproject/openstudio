import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"



class CustomerDisplayClasscards extends Component {
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

    formatClassesRemaining(card) {
        let return_value
        if (card.Unlimited) {
            return_value = "Unlimited classes"
        } else {
            let class_string = 'classes'
            if (card.classes_remaining == 1) {
                class_string = 'class'
            } 
            return_value = card.classes_remaining + ' ' + class_string + ' remaining'
        }

        return return_value
    }


    render() {
        const customerID = this.props.customerID
        const classcards = this.props.classcards

        return (
           <div>
               { (classcards.loaded) ?
                (classcards.data.length) ?
                    <div>     
                        <b>Class cards</b>
                        {classcards.data[customerID].map((classcard, i) => 
                            <div key={v4()}>
                                { classcard.name } <br />
                                <span className="text-muted">
                                    { classcard.start }
                                    { (classcard.end) ? " - " + classcard.end : ''} <br/>
                                    {this.formatClassesRemaining(classcard)}
                                </span>
                            </div>
                        )}
                    </div> : '' 
                : "Loading classcards, please wait..."
               }
           </div>
        )
    }
}

export default CustomerDisplayClasscards

