import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import PageTemplate from "../../components/PageTemplate"


class homeComponent extends Component {
    constructor(props) {
        super(props),
        this.videoStream = React.createRef()
        this.snap = React.createRef()
        this.superSecretPictureCanvas = React.createRef()
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app_state: PropTypes.object,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.home.page_title' })
        )
    }

    onClickStartCamera() {
        console.log('Home component DidMount')
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

    onClickTakePhoto() {
        console.log('say cheese!!')
        var snap = this.takeSnapshot();

        // Show image. 
        this.snap.current.setAttribute('src', snap);
        // image.classList.add("visible");

        // Enable delete and save buttons
        // delete_photo_btn.classList.remove("disabled")
        // download_photo_btn.classList.remove("disabled")

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
            return hidden_canvas.toDataURL('image/png');
        }
    }


    render() {
        return (
            <PageTemplate app_state={this.props.app}>
                <section className="Welcome">
                    {/* <div>{this.props.app.loading}</div>
                    <div>{this.props.app.loading_message}</div> */}
                    {this.props.intl.formatMessage({ id: 'app.pos.home.hello' })}

                    <div className="camera-app">
                        <button id="start-camera" 
                                className="visible"
                                onClick={this.onClickStartCamera.bind(this)}
                                >
                            Touch here to start the camera.
                        </button>
                        <video id="camera-stream" 
                               autoPlay 
                               ref={this.videoStream}></video>
                        <img ref={this.snap} id="snap" />

                        <p id="error-message"></p>

                        <div className="controls">
                            <button id="delete-photo" title="Delete Photo" className="disabled"><i className="fa fa-ban"></i></button>
                            <button id="take-photo" onClick={this.onClickTakePhoto.bind(this)} title="Take Photo"><i className="fa fa-camera"></i></button>
                            <button id="download-photo" download="selfie.png" title="Save Photo" className="disabled"><i className="fa fa-save"></i></button>  
                        </div>

                        {/* <!-- Hidden canvas element. Used for taking snapshot of video. --> */}
                        <canvas ref={this.superSecretPictureCanvas}></canvas>
                    </div>
                </section>
            </PageTemplate>
        )
    }
}

export default homeComponent
