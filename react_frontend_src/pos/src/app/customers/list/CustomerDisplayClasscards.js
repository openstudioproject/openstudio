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
        console.log(card)
        if (card.unlimited) {
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
        const data = this.props.data
        const classcards = data.data.classcards

        return (
           <div>
               { (data.loaded) ?
                (classcards.length) ?
                    <div>     
                        <b>Class cards</b>
                        {classcards.map((classcard, i) => 
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

