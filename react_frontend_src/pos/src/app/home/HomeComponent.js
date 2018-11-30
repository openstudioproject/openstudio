import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import PageTemplate from "../../components/PageTemplate"


class homeComponent extends Component {
    constructor(props) {
        super(props),
        this.videoStream = React.createRef()
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
                        <img id="snap" />

                        <p id="error-message"></p>

                        <div className="controls">
                        <a href="#" id="delete-photo" title="Delete Photo" className="disabled"><i className="material-icons">delete</i></a>
                            <a href="#" id="take-photo" title="Take Photo"><i className="material-icons">camera_alt</i></a>
                            <a href="#" id="download-photo" download="selfie.png" title="Save Photo" className="disabled"><i className="material-icons">file_download</i></a>  
                        </div>

                        {/* <!-- Hidden canvas element. Used for taking snapshot of video. --> */}
                        <canvas></canvas>
                    </div>
                </section>
            </PageTemplate>
        )
    }
}

export default homeComponent
