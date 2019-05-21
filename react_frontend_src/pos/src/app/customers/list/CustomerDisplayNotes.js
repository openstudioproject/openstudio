import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"
import { confirmAlert } from 'react-confirm-alert' // Import


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

    onDelete = (customerID, noteID) => {
        confirmAlert({
            title: 'Confirm to delete',
            message: 'Are you sure to delete this note?',
            buttons: [
                {
                label: 'Yes, delete it',
                onClick: () => {
                    this.props.onClickDeleteNote(customerID, noteID)
                }},
                {
                label: 'No, keep it',
                // onClick: () => alert('Click No')
                }
            ]
            })
    }
    

    render() {
        const customerID = this.props.customerID
        const customers = this.props.customers
        const notes = customers.notes
        const notes_loaded = customers.notes_loaded

        return (
           <div>
               { (notes_loaded) ?
                (customers.has_unacknowledged_notes) ? 
                    <div>
                        <b>Notes</b>
                        <div>unack notes found!</div>
                    </div> :
                    (notes.data) ?
                        <div>     
                            <b>Notes</b>
                            {console.log(notes.data)}
                            <div className="direct-chat-messages">
                            {notes.data.map((note, i) => 
                                <div key={v4()}>                               
                                    <div className="direct-chat-msg">
                                        <div className="direct-chat-info clearfix">
                                        <span className="direct-chat-name pull-left">{note.User}</span>
                                            <span 
                                            className="btn btn-xs btn-danger direct-chat-scope pull-right" 
                                            onClick={() => this.onDelete(customerID, note.id)}>
                                                <i className="fa fa-pencil" />  Delete note
                                            </span>
                                            <span 
                                            className="btn btn-xs btn-default direct-chat-scope pull-right" 
                                            onClick={() => this.props.OnClickUpdateNote(note.id)}>
                                                <i className="fa fa-pencil" />  Edit note
                                            </span>
                                            <span className="direct-chat-timestamp pull-right">{note.Timestamp} {note.Time}</span>
                                        </div>
                                        <img className="direct-chat-img" src="/static/images/person_inverted_small.png" alt="" />
                                        <div className="direct-chat-text">
                                            {note.Note}
                                        </div>
                                    </div>
                                </div>
                            )}
                            </div>
                        </div> : '' 
                : "Loading notes, please wait..."
               }
           </div>
        )
    }
}

export default CustomerDisplayNotes