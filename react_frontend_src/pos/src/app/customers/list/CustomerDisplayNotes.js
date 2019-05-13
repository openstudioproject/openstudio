import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"



class CustomerDisplayNotes extends Component {
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
        const customers = this.props.customers
        notes = customers.notes
        notes_loaded = customers.notes_loaded
        notes_loading = customers.notes_loading

        return (
           <div>
               { (notes_loaded) ?
                (notes.data) ?
                    <div>     
                        <b>Notes</b>
                        {console.log(notes.data)}
                        {/* {classcards.data[customerID].map((classcard, i) => 
                            <div key={v4()}>
                                { classcard.name } <br />
                                <span className="text-muted">
                                    { classcard.start }
                                    { (classcard.end) ? " - " + classcard.end : ''} <br/>
                                    {this.formatClassesRemaining(classcard)}
                                </span>
                            </div>
                        )} */}
                    </div> : '' 
                : "Loading notes, please wait..."
               }
           </div>
        )
    }
}

export default CustomerDisplayNotes