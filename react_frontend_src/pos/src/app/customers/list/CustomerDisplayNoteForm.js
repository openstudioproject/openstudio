import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"
import Inputmask from "inputmask"
// import Inputmask from "inputmask/dist/inputmask/inputmask.date.extensions";

import CustomerFormError from "./CustomerFormError"


class CustomerDisplayNoteForm extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
    }

    render() {
        const title = this.props.title
        const error_data = this.props.errorData
        const onSubmit = this.props.onSubmit
        const onCancel = this.props.onClickCancel

        return (
            <div>
                <label htmlFor="CustomersNoteTextarea">{title}</label>
                <form onSubmit={onSubmit}>
                    <textarea
                        id="CustomersNoteTextarea" 
                        className="form-control"
                        name="Note" 
                    />
                    <CustomerFormError message={ (error_data.Note) ? error_data.Note : "" } /> 
                    <br />
                    <button className="btn btn-primary pull-right">Save</button>
                </form>
                <button className="btn btn-link" onClick={onCancel.bind(this)}>Cancel</button>
            </div>
        )
    }
}

export default CustomerDisplayNoteForm

