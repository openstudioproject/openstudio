import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"
import validator from 'validator'
import { v4 } from "uuid"

import ButtonCustomerEdit from "../../../components/ui/ButtonCustomerEdit"

const CustomerDisplay = ({customerID, customers, edit_in_progress, onClickEdit=f=>f}) => 
    <div>
        { !(customerID) || (edit_in_progress) ? null :
        <div className="box box-solid"> 
            <div className="box-header">
                <h3 className="box-title">Customer</h3>
            </div>
            <div className="box-body">
                <div className="col-md-6">
                    <div class="app">
                        <a href="#" id="start-camera" class="visible">Touch here to start the app.</a>
                        <video id="camera-stream"></video>
                        <img id="snap" />

                        <p id="error-message"></p>

                        <div class="controls">
                          <a href="#" id="delete-photo" title="Delete Photo" class="disabled"><i class="material-icons">delete</i></a>
                            <a href="#" id="take-photo" title="Take Photo"><i class="material-icons">camera_alt</i></a>
                            <a href="#" id="download-photo" download="selfie.png" title="Save Photo" class="disabled"><i class="material-icons">file_download</i></a>  
                        </div>

                        {/* <!-- Hidden canvas element. Used for taking snapshot of video. --> */}
                        <canvas></canvas>
                    </div>
                </div>
                <div className="col-md-6">
                    {customers[customerID].display_name}
                    {customers[customerID].address}
                    <ButtonCustomerEdit onClick={onClickEdit}/>
                </div>
            </div>
        </div>
        }
    </div>


export default CustomerDisplay
