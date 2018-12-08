import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"

import ButtonCustomerEdit from "../../../components/ui/ButtonCustomerEdit"


class CustomerDisplay extends Component {
    constructor(props) {
        super(props)
        console.log("Customer display props:")
        console.log(props)
        this.videoStream = React.createRef()
        this.superSecretPictureCanvas = React.createRef()
    }

    PropTypes = {
        intl: intlShape.isRequired,
        customerID: PropTypes.integer,
        customers: PropTypes.object,
        edit_in_progress: PropTypes.boolean,
        onClickEdit: PropTypes.function
    }


    onClickStartCamera() {
        console.log('Customer Display component DidMount')
        this.props.onClearCameraAppSnap()
        // var constraints = { audio: false, video: { facingMode: 'user' } }
        if (navigator.mediaDevices.getUserMedia) {       
            navigator.mediaDevices.getUserMedia({video: true})
          .then(stream => {
            this.videoStream.current.srcObject = stream
          })
          .catch(error => {
            console.log("Something went wrong while trying to stream video!");
            console.log(error)
          });
        }
    }

    onClickRedoPhoto() {
        console.log("another day, another chance")
        this.props.onClearCameraAppSnap()
        this.videoStream.current.play()
    }

    onClickSavePhoto() {
        console.log("saved for eternity")

        this.props.onSaveCameraAppSnap(
            this.props.customers.displayID,
            this.props.customers.camera_app_snap
        )

        document.getElementById("btnCloseModal").click()

        // Stop video playback of stream.
        var tracks = this.videoStream.current.srcObject.getTracks()
        var i
        for (i = 0; i < tracks.length; i++) {
            tracks[i].stop()
        }
    }

    onClickTakePhoto() {
        console.log('say cheese!!')
        var snap = this.takeSnapshot()
        console.log(snap)

        // Show image. 

        // Set the href attribute of the download button to the snap url.
        // download_photo_btn.href = snap

        // Pause video playback of stream.
        this.videoStream.current.pause()
    }


    takeSnapshot(){
        // Here we're using a trick that involves a hidden canvas element.  
        var video = this.videoStream.current
        var hidden_canvas = this.superSecretPictureCanvas.current
        var context = hidden_canvas.getContext('2d');

        var width = video.videoWidth
        var height = video.videoHeight

        if (width && height) {

            // Setup a canvas with the same dimensions as the video.
            hidden_canvas.width = width;
            hidden_canvas.height = height;

            // Make a copy of the current frame in the video on the canvas.
            context.drawImage(video, 0, 0, width, height);

            // Turn the canvas image into a dataURL that can be used as a src for our photo.
            this.props.onSetCameraAppSnap(hidden_canvas.toDataURL('image/png'))
            return hidden_canvas.toDataURL('image/png')
        }
    }


    render() {
        const customerID = this.props.customerID
        const customers = this.props.customers
        const customers_list = this.props.customers.data
        const edit_in_progress = this.props.edit_in_progress
        const onClickEdit = this.props.onClickEdit
        let videoClass
        let imgClass

        !(customers.camera_app_snap) ?
             imgClass = 'hidden' : videoClass = 'hidden'

        return (
            <div>
                { !(customerID) || (edit_in_progress) ? null :
                <div className="box box-solid"> 
                    <div className="box-header">
                        <h3 className="box-title">{customers_list[customerID].display_name}</h3>
                    </div>
                    <div className="box-body">
                        <div className="col-md-3">
                            <div className="customer-display-image">
                                <img src={customers_list[customerID].thumblarge}
                                     alt={customers_list[customerID].display_name} />
                            </div><br />
                            <button type="button" 
                                    onClick={this.onClickStartCamera.bind(this)} 
                                    className="btn btn-default" 
                                    data-toggle="modal" 
                                    data-target="#cameraModal">
                                <i className="fa fa-camera"></i> Take picture
                            </button>

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
                        <div className="col-md-9">
                            <ButtonCustomerEdit onClick={onClickEdit}
                                                classAdditional='pull-right'>
                                { ' ' } Edit
                            </ButtonCustomerEdit>
                            <label>Name</label><br/>
                            {customers_list[customerID].display_name}<br/>
                            <label>Email</label><br/>
                            {customers_list[customerID].email}<br/>
                            {/* <label>Address</label><br/>
                            {customers_list[customerID].address}<br/> */}
                        </div>
                    </div>
                </div>
                }
            </div>
        )
    }
}

export default CustomerDisplay

