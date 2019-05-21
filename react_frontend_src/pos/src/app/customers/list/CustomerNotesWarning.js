import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"
import { Link } from 'react-router-dom'

import ButtonCustomerEdit from "../../../components/ui/ButtonCustomerEdit"
// import CustomerDisplayMemberships from "./CustomerDisplayMemberships"
// import CustomerDisplaySubscriptions from "./CustomerDisplaySubscriptions"
// import CustomerDisplayClasscards from "./CustomerDisplayClasscards"
// import CustomerDisplayNotes from "./CustomerDisplayNotes"
// import CustomerDisplayNoteForm from "./CustomerDisplayNoteForm"


class CustomerNotesWarning extends Component {
    constructor(props) {
        super(props)
        console.log("Customer display props:")
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
    }


    render() {
        const customerID = this.props.customerID
        const customers = this.props.customers
        const customers_list = this.props.customers.data
        const has_unacknowledged_notes = customers.has_unacknowledged_notes
        const memberships = this.props.memberships
        const subscriptions = this.props.subscriptions
        const classcards = this.props.classcards
        const edit_in_progress = this.props.edit_in_progress
        const onClickEdit = this.props.onClickEdit
        let videoClass
        let imgClass

        

        !(customers.camera_app_snap) ?
             imgClass = 'hidden' : videoClass = 'hidden'

        let link_checkin
        (has_unacknowledged_notes) ? link_checkin = "/customer/notes_warning": link_checkin = "/classes/" + customerID
        console.log('has_unacknowledged_notes')
        console.log(has_unacknowledged_notes)

        return (
            <div>
                { !(customerID) || (edit_in_progress) ? null :
                <div className="box box-solid"> 
                    <div className="box-header">
                        <h3 className="box-title">{customers_list[customerID].display_name}</h3>
                    </div>
                    <div className="box-body">
                        <div className="col-md-2">
                            <div className="customer-display-image">
                                <img src={customers_list[customerID].thumblarge}
                                     alt={customers_list[customerID].display_name} />
                            </div><br />
                            {/* <!-- Modal --> */}
                            <div className="modal fade" id="cameraModal" tabIndex="-1" role="dialog" aria-labelledby="myModalLabel" ref={this.modal}>
                                <div className="modal-dialog" role="document">
                                    <div className="modal-content">
                                        <div className="modal-header">
                                            <button type="button" className="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                                            <h4 className="modal-title" id="myModalLabel">Take picture for {customers_list[customerID].display_name}</h4>
                                        </div>
                                        <div className="modal-body">
                                            {/* Camera app */}
                                            <div className="camera-app">
                                                {/* <button id="start-camera" 
                                                        className="visible btn btn-default"
                                                        onClick={this.onClickStartCamera.bind(this)} >
                                                    Start camera
                                                </button> */}
                                                {/* Shop video stream when no snapshot has been taken from the camera. Otherwise show snapshot image */}
                                                <video id="camera-stream" 
                                                    className={videoClass}
                                                    autoPlay 
                                                    ref={this.videoStream} />
                                                <img id="snap" 
                                                    className={imgClass}
                                                    src={customers.camera_app_snap} />

                                                <p id="error-message"></p>

                                                {/* <!-- Hidden canvas element. Used for taking snapshot of video. --> */}
                                                <canvas ref={this.superSecretPictureCanvas}></canvas>
                                            </div>
                                            {/* Close camera app */}
                                        </div>
                                        {/* Close modal body */}
                                        <div className="modal-footer">
                                                {!(customers.camera_app_snap) ?
                                                        <button id="take-photo" 
                                                                className="btn btn-primary"
                                                                onClick={this.onClickTakePhoto.bind(this)} 
                                                                title="Take Photo">
                                                            <i className="fa fa-camera"></i>
                                                            { ' ' } Take picture
                                                        </button>
                                                    : 
                                                    <span>
                                                            <button id="redo-photo" 
                                                                    title="redo Photo" 
                                                                    className="btn btn-default"
                                                                    onClick={this.onClickRedoPhoto.bind(this)}>
                                                                <i className="fa fa-repeat"></i>
                                                                { ' ' } Redo picture
                                                            </button>        
                                                            <button id="download-photo" 
                                                                    download="selfie.png" 
                                                                    title="Save Photo" 
                                                                    className="btn btn-primary"
                                                                    onClick={this.onClickSavePhoto.bind(this)}>
                                                                <i className="fa fa-save"></i>
                                                                { ' ' } Save picture
                                                            </button>          
                                                    </span>
                                                }
                                            <button type="button" id="btnCloseModal" className="btn btn-default pull-left" data-dismiss="modal">Close</button>
                                        </div> 
                                        {/* Close modal footer */}
                                    </div>
                                    {/* Close modal content */}
                                </div>
                                {/* Close modal-dialog */}
                            </div> 
                            {/* Close modal */}
                        </div> 
                        {/* Close md-4 */}
                        <div className="col-md-8">
                            <div className="col-md-3">
                                <label>Name</label><br/>
                                {customers_list[customerID].display_name}<br/>
                                <label>Email</label><br/>
                                {customers_list[customerID].email}<br/>
                                <label>Phone</label><br/>
                                {customers_list[customerID].mobile}<br/>
                                <label>Date of birth</label><br/>
                                {customers_list[customerID].date_of_birth}<br/>
                            </div>
                            <div className="col-md-3">
                                <CustomerDisplayMemberships customerID={customerID}
                                                            memberships={memberships}/>
                                <CustomerDisplaySubscriptions customerID={customerID}
                                                              subscriptions={subscriptions}/>
                                <CustomerDisplayClasscards customerID={customerID}
                                                           classcards={classcards}/>
                            </div>
                            <div className="col-md-6">
                                {((customers.create_note) || (customers.update_note)) ?
                                    (customers.create_note) ?
                                        // Create note
                                        <CustomerDisplayNoteForm
                                            title="Add note" 
                                            errorData={this.props.createNoteErrorData}
                                            onSubmit={this.onCreateNote.bind(this)}
                                            onClickCancel={this.props.onClickCancelCreateNote}
                                        /> :
                                        // Update note
                                        <CustomerDisplayNoteForm
                                            title="Edit note" 
                                            update={true}
                                            notes={customers.notes}
                                            selectedNoteID={customers.selected_noteID}
                                            errorData={this.props.updateNoteErrorData}
                                            onSubmit={this.onUpdateNote.bind(this)}
                                            onClickCancel={this.props.OnClickCancelUpdateNote}
                                        />
                                    :
                                    <CustomerDisplayNotes 
                                        customers={customers} 
                                        customerID={customers.displayID}
                                        OnClickUpdateNote={this.props.OnClickUpdateNote}
                                        onClickDeleteNote={this.props.onClickDeleteNote}
                                    />
                                }
                            </div>
                        </div>
                        <div className="col-md-2">
                            <a href={`/customers/barcode_label?cuID=${customerID}`}
                               className="btn btn-default btn-flat btn-block"
                               target="_blank">
                                <i className="fa fa-id-card-o"></i> Print card   
                            </a>
                            <button type="button" 
                                    onClick={this.onClickStartCamera.bind(this)} 
                                    className="btn btn-default btn-flat btn-block" 
                                    data-toggle="modal" 
                                    data-target="#cameraModal">
                                <i className="fa fa-camera"></i> Take picture
                            </button> 
                            <Link to={link_checkin}
                                  className="btn btn-default btn-flat btn-block">
                                <i className="fa fa-check-square-o"></i> Class check-in
                            </Link>
                            <button type="button" 
                                    onClick={this.props.onClickCreateNote.bind(this)} 
                                    className="btn btn-default btn-flat btn-block">
                                <i className="fa fa-sticky-note-o"></i> Add note
                            </button>
                            <ButtonCustomerEdit onClick={onClickEdit}
                                                classAdditional='btn-flat btn-block'>
                                { ' ' } Edit customer
                            </ButtonCustomerEdit>
                        </div>
                    </div>
                </div>
                }
            </div>
        )
    }
}

export default CustomerNotesWarning